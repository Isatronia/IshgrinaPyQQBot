# -*- encoding: utf-8 -*-
'''
@File    :   AppiumQQBot.py
@Contact :   naragnova88@gmail.com
@License :   CC BY-NC-SA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/27 9:28    naragNova     1.0         None
'''
import ctypes
import inspect
import os
import random
import re
import time
from traceback import format_exc as getTraceback

import cv2
import numpy as np
from appium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

import chatbot_core as chatbot

# debug level:
# DEBUG     3
# INFO      2
# WARNING   1
# ERROR     0
__DEBUG_LEVEL__ = 5
__DEBUG_STR_ = [
    '[ERROR] ',
    '[WARN]  ',
    '[INFO]  ',
    '[DEBUG] '
]

LOG_PATH = os.getcwd() + '\\log\\' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.botlog'
CHAT_PATH: str = os.getcwd() + '\\chat\\' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.chat'
IMG_PATH: str = os.getcwd() + '\\Img\\'
CAPTURE_PATH: str = IMG_PATH + 'capture\\'
STORE_PATH: str = os.getcwd() + '\\src\\'

# 汉字过滤
re_sub = u"([^\u4e00-\u9fa5\u0020-\u007e\u3001-\u3002\u300a-\u300b\u301c\uff01-\uff5e\uff61\uff64])"


def log(s, level: int = 3) -> None:
    """
    logger used in PyBot Project
    :param s: string to log
    :param level: log level (0 - Error, 1 - Warning, 2 - Info, 3 - Debug), default Debug.
    :return: None
    """
    global __DEBUG_LEVEL__, __DEBUG_STR_, LOG_PATH
    s = str(s)
    if __DEBUG_LEVEL__ >= level >= 0:
        level = min(3, level)
        log_info = (__DEBUG_STR_[level] + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + ':' + s)
        print(log_info)
        logger = open(LOG_PATH, mode='a', encoding='utf-8')
        logger.write(log_info + '\n')
        logger.close()
    return


def print_stack_trace(level: int = 0) -> None:
    """
    print stack trace, default level is ERROR
    :param level: log level
    :return: None
    """
    log(getTraceback(), level)
    return


def prefix_function(s1: list, s2: list):
    """
    cal Prefix array of a string, but now we should use this to calculate the hash value of two string lists.
    :param s1: string list 1
    :param s2: string list 2
    :return:
    """
    n = min(len(s1), len(s2))
    pi = [0] * n
    for i in range(1, n):
        j = pi[i - 1]
        while j > 0 and s1[i] != s2[j]:
            j = pi[j - 1]
        if s1[i] == s1[j]:
            j += 1
        pi[i] = j
    return pi


class PyBot:
    """
    PyBot
    a simple QQ Bot By Python\n
    Base on Appium, please change desired_caps setting to fit your system before init this bot.\n
    Appium Required, please install that first
    """
    # define Debug Level
    ULTRA_DEBUG = 4
    DEBUG = 3
    INFO = 2
    WARNING = 1
    ERROR = 0

    # time gap between message reading
    readInfoDelay = 0.5

    # run configurations
    __DEBUG_FLAGS__ = set()

    # caps
    desired_caps_Simulator = {
        "platformName": "Android",
        "plantformVersion": "7",
        "deviceName": "Ishgrina",
        "appPackage": 'com.tencent.mobileqq',
        "appActivity": '.activity.SplashActivity',
        "unicodeKeyboard": True,
        "resetKeyboard": True,
        "noReset": True,
        "newCommandTimeout": 6000
    }
    desired_caps_Real = {
        "platformName": "Android",
        "plantformVersion": "8",
        "deviceName": "Ishgrina",
        "appPackage": 'com.tencent.mobileqq',
        "appActivity": '.activity.SplashActivity',
        "unicodeKeyboard": True,
        "resetKeyboard": True,
        "noReset": True,
        "newCommandTimeout": 6000
    }

    class BotStopSign(BaseException):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    class AccessDeniedError(ValueError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    class ApplicationStoppedError(ValueError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    class TargetGroupImageNotFoundError(ValueError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __init__(self, caps=None) -> None:
        """
        class initialize function
        :param caps: the desired_capabilities to connect Appium
        """
        if caps is None:
            # default using real phone.
            caps = self.desired_caps_Real
        self.desired_caps = caps
        self.Reply = dict()
        self.lastMsgList = []
        self.runEnvironment = 'Prd'
        self.firewall = {'import', 'from', 'open', 'np', 'os', '='}

        self.__config = dict()
        # default config.
        self.config('appium_url', 'http://localhost:4723/wd/hub')
        self.config('code_prefix', 'py')

        # messageProc -- message process Class
        self.messageProc = None
        self.bot = None
        self.bot_name = '澪依'
        return

    def set_bot_name(self, name: str) -> None:
        self.bot_name = name

    def add_control_flag(self, flag: str = ''):
        """
        addDebugFlag\n
        allowed flags: \n
        :param   :\n
        - allow_exec --     allow bot reply functions. *Warning* this may hurt your server.\n
        - no_chat --        disable bot's chat, still reply code.\n
        - no_reply --       disable bot's reply, bot will be silent\n
        - record_chat --    save chat to a specific path\n
        """
        self.__DEBUG_FLAGS__.add(flag)
        log('Added a Debug Flag:' + flag, PyBot.INFO)
        return

    def config(self, key: str, value: str) -> None:
        """
        config\n
        :param value:
        - appium_url : the appium's url to connect.\n
        - code_prefix : if bot see this prefix, it will process this message as a code.\n
        - code_split_char : split args in a function-run command, default "."\n
        :param key: config item
        """
        self.__config[key] = value

    def remove_control_flag(self, flag: str = ''):
        """
        remove_control_flag
        :param flag: control flag
        :return: None
        """
        if flag in self.__DEBUG_FLAGS__:
            self.__DEBUG_FLAGS__.remove(flag)
        return

    # Different hash algorithm, returns the hash value of the map
    @staticmethod
    def __cal_d_hash_from_cv2_image(img) -> str:
        """
        cal_d_hash_from_cv2_image
        :param img:
        :return: D-Hash value of an image.
        """
        img = cv2.resize(img, (9, 8), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        d_hash_str, result = '', ''
        for i in range(8):
            for j in range(8):
                if gray[i, j] > gray[i, j + 1]:
                    d_hash_str = d_hash_str + '1'
                else:
                    d_hash_str = d_hash_str + '0'
        for i in range(0, 64, 4):
            result += ''.join('%x' % int(d_hash_str[i:i + 4], 2))
        return result

    # calculate Hamming Distance 
    def __cal_hamming_distance(self, img1: object, img2: object) -> int:
        """
        The Hamming Distance of these two images; Calculated by Different hash algorithm.
        :param img1: open-cv Image
        :param img2: open-cv Image
        :return: hamming distance between two images.
        """
        hash1 = self.__cal_d_hash_from_cv2_image(img1)
        hash2 = self.__cal_d_hash_from_cv2_image(img2)
        if len(hash1) != len(hash2):
            log('Can NOT compare hash if they have different length!!!', PyBot.ERROR)
            return -1
        n = 0
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                n = n + 1
        return n

    def __delete_repeated_messages(self, text_list: list) -> list:
        """
        delete_repeated_messages
        :param text_list: received message list.
        :return: list without repeated messages.
        """
        if not hasattr(self, 'lastMsgList'):
            return text_list
        if len(text_list) == 0:
            return []
        res, i, j, length = [], 0, 0, min(len(self.lastMsgList), len(text_list))
        for i in range(length):
            if self.lastMsgList[i] == text_list[0]:
                for j in range(length - i):
                    if self.lastMsgList[i + j] != text_list[j]:
                        j -= 1
                        break
                if i + j + 1 >= length:
                    break
        for j in range(len(text_list) - i, len(text_list)):
            res.append(text_list[j])
        self.lastMsgList = text_list
        return res

    def botReply(self, question):
        log('sending quest: ' + question)
        self.bot.quest(question)

    # reply a message
    def __reply_message(self, text: str) -> None:
        """
        replyMessage
        :param text: text to reply
        """
        if 'no_chat' not in self.__DEBUG_FLAGS__:
            if self.bot_name in text:
                text = re.sub(re_sub, '', text)
                self.botReply(text)
        text = text.split(' ')
        if len(text) > 1:
            if text[0] == self.__config['code_prefix']:
                self.__py_code_process(text[1])
        return

    # connect to Appium
    def __connect_appium(self) -> None:
        """
        Connect to Appium.
        :return: None
        """
        try:
            self.driver = webdriver.Remote(self.__config['appium_url'], self.desired_caps)
            self.driver.implicitly_wait(10)
        except KeyError:
            log('Connect Error, please check if appium url is wrong.', PyBot.ERROR)
            print_stack_trace()

    # Send a message to current chat.
    def __send_message(self, msg: str) -> bool:
        """
        send a simple text message to current chat.
        :param msg: message to send.
        """
        try:
            sender = self.driver.find_element_by_id('com.tencent.mobileqq:id/input')
            send_button = self.driver.find_element_by_id("com.tencent.mobileqq:id/fun_btn")
            sender.send_keys(msg)
            send_button.click()
            log('Send Message: ' + msg, PyBot.INFO)
            return True
        except Exception as e:
            log(e)
            print_stack_trace()
            return False

    # Get texts from chat
    def __get_texts(self) -> list:
        """
        :return: text list in current chat
        """
        res = []
        texts = self.driver.find_elements_by_id('com.tencent.mobileqq:id/chat_item_content_layout')
        for t in texts:
            res.append(t.text)
        if len(res) == 0:
            raise PyBot.ApplicationStoppedError("App maybe stopped, retry connection.")
        return res

    def __setup_reply_dict_by_file(self, path: str = 'src\\BotReply.reply') -> None:
        """
        Set up pre-defined reply messages from a file.
        :param path: path of pre-defined replies.
        """
        try:
            reader = open(path, mode='r', encoding='utf-8')
            lines = reader.read().split('\n')
            for line in lines:
                line = line.split('@')
                if len(line) >= 2:
                    self.Reply[line[0]] = line[1]
                    log('will reply ' + line[0] + ' with ' + line[1])
            reader.close()
        except FileNotFoundError:
            log('No Config File Found!', self.WARNING)
            self.Reply = dict()
        return

    def __py_code_check(self, code: str) -> any:
        """
        # pyCodeCheck\n
        :param code : Code to check\n
        Description:\n
        Check if run this code will cause some problem to your PC.\n
        if check failed, raise *PyBot.AccessDeniedError*
        """
        if 'allow_exec' not in self.__DEBUG_FLAGS__:
            raise PyBot.AccessDeniedError('notAllowed')
        for chk in self.firewall:
            if chk in code:
                log('someone want attack bot with code : ' + code, PyBot.WARNING)
                raise PyBot.AccessDeniedError('code')
        return code

    def __py_code_process(self, code: str) -> any:
        """
        :param code: python code to run
        """
        try:
            log('Running Code :' + code, PyBot.INFO)
            code = self.__py_code_check(code)
            if not 'code_split_char' in self.__config:
                self.__config['code_split_char'] = '.'
            code = code.split(self.__config['code_split_char'])
            if hasattr(self.messageProc, code[0]):
                func = getattr(self.messageProc, code[0])
                self.__send_message(func(code[1:]))
        except PyBot.AccessDeniedError:
            self.__send_message('访问被拒绝')
        except Exception as e:
            log('Code Run Error', PyBot.WARNING)
            log(e)
            print_stack_trace(PyBot.WARNING)
            self.__send_message('你写的是个鬼代码')
        pass

    # mainProcess
    def main_process(self) -> None:
        """
        # mainPrc\n
        ---
        @Description:\n
        Do Main Process here.
        """
        global CHAT_PATH
        try:
            try:
                text_list = self.__delete_repeated_messages(self.__get_texts())
            except StaleElementReferenceException:
                log("Get Text failed, this may cause by StaleElementReferenceException. Reloading.")
                time.sleep(random.random())
                text_list = self.__delete_repeated_messages(self.__get_texts())
        except StaleElementReferenceException:
            log("Still failed, skip this message reading.")
            return
        if len(text_list):
            log('Process Message List:' + str(text_list), PyBot.DEBUG)
            if 'record_chat' in self.__DEBUG_FLAGS__:
                logger = open(CHAT_PATH, mode='a', encoding='utf-8')
                for txt in text_list:
                    if txt != '':
                        logger.write(time.asctime(time.localtime(time.time())) + ' ' + txt + '\n')
                logger.close()
        if 'no_reply' in self.__DEBUG_FLAGS__:
            log('No reply', PyBot.DEBUG)
            return
        for txt in text_list:
            self.__reply_message(txt)
        while len(self.bot.answer):
            self.__send_message(self.bot.get_ans())
        return

    def __get_target_group_image(self):
        global IMG_PATH
        target_group_img = None
        log("opening target Img")
        try:
            if self.runEnvironment == 'Prd':
                target_group_img = cv2.imread(IMG_PATH + 'target.png')
            elif self.runEnvironment == 'Dev':
                target_group_img = cv2.imread(IMG_PATH + 'target_test.png')
        except Exception as e:
            log(e, PyBot.ERROR)
            print_stack_trace()
            raise PyBot.TargetGroupImageNotFoundError("Target Group Image not found")
        if target_group_img is None:
            raise PyBot.TargetGroupImageNotFoundError("Target Group Image not found")
        return target_group_img

    def __enter_target_group(self, target_group_img):
        """
        enter target group, if no target image, raise ValueError
        :param target_group_img:
        :return:
        """
        if target_group_img is None:
            raise PyBot.TargetGroupImageNotFoundError("Target Group Image not found")
        images = self.driver.find_elements_by_id('com.tencent.mobileqq:id/icon')
        for img in images:
            screenshot_img = cv2.imdecode(np.frombuffer(img.screenshot_as_png, np.uint8), cv2.IMREAD_COLOR)
            if self.__cal_hamming_distance(target_group_img, screenshot_img) < 5:
                img.click()
                return
        raise PyBot.TargetGroupImageNotFoundError("Target Group Not Found. Please check capture path and select a "
                                                  "screenshot as target.png, save that in Img path. Make sure u can "
                                                  "always see that group when app start")
        return

    def init(self, reconnect: bool = False):
        # 链接Appium
        self.__connect_appium()
        if self.driver is None:
            raise KeyError('No Device connected')

        # maybe there will show up a dialog, close that.
        bja = self.driver.find_elements_by_id('com.tencent.mobileqq:id/bja')
        if len(bja):
            self.driver.find_elements_by_id('com.tencent.mobileqq:id/az7')[0].click()

        self.__enter_target_group(self.__get_target_group_image())
        if reconnect:
            return
        if 'chatbot' in self.__DEBUG_FLAGS__ and self.bot is None:
            self.bot = chatbot.ChatBot()
            self.bot.start()
        self.__setup_reply_dict_by_file()

    # Run bot!
    def run(self) -> None:
        log('Starting Bot', self.INFO)

        try:
            self.init()
        except NameError as e:
            log(str(e), PyBot.ERROR)
            log(getTraceback(), PyBot.ERROR)
            return

        log('Bot Init Done, Start Listening.', self.INFO)
        if 'no_run' in self.__DEBUG_FLAGS__:
            return
        while True:
            try:
                self.main_process()
            except PyBot.ApplicationStoppedError as e:
                print(e)
                self.init(reconnect=True)
            time.sleep(self.readInfoDelay)

    def capture_group_image(self) -> None:
        """
        capture chat group icon
        :return: None
        """
        global CAPTURE_PATH
        if self.driver is None:
            self.__connect_appium()
        chats = self.driver.find_elements_by_id('com.tencent.mobileqq:id/icon')
        ind = 0
        if not os.path.exists(CAPTURE_PATH):
            os.makedirs(CAPTURE_PATH)
        for i in chats:
            img = cv2.imdecode(np.frombuffer(i.screenshot_as_png, np.uint8), cv2.IMREAD_COLOR)
            fname = CAPTURE_PATH + str(ind) + '.png'
            cv2.imwrite(fname, img)
            ind = ind + 1
        return

    def _async_raise(self, tid, exctype):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def close(self):
        if self.bot is not None:
            self.stop_thread(self.bot)
