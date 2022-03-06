# -*- encoding: utf-8 -*-
'''
@File    :   corpusGenerator.py
@Contact :   naragnova88@gmail.com
@License :   CC BY-NC-SA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/1 9:28    naragNova     1.0         None
'''

# import lib
import os
import re

import jieba
import wordcloud

CHAT_PATH: str = os.getcwd() + '\\chat\\'
CORPUS_PATH: str = os.getcwd() + '\\chatbot\\corpus\\'

USER_DICT_PATH: str = CORPUS_PATH + 'user_dict.dict'
CORPUS_FILE_NAME = 'groupChatRec'


def get_corpus_from_chat(files: list = None, keep_ori: bool = False) -> list:
    if files is None:
        files = []
        for root, dirs, file in os.walk(CHAT_PATH):
            files = file

    corpus = []
    for f_name in files:
        with open(CHAT_PATH + f_name, mode='r', encoding='utf-8') as f_obj:
            for line in f_obj.readlines():
                line = line.rstrip()
                line = line.lstrip('\ufeff')
                if not keep_ori:
                    line = line.split(' ')[-1]
                    line = re.sub(
                        u"([^\u4e00-\u9fa5\u0020-\u007e\u3001-\u3002\u300a-\u300b\u301c\uff01-\uff5e\uff61\uff64])", "",
                        line)
                if len(line):
                    corpus.append(line)
    return corpus


def gen_corpus():
    corpus = get_corpus_from_chat()

    jieba.load_userdict(USER_DICT_PATH)
    corpus_writer = open(CORPUS_PATH + CORPUS_FILE_NAME + '.txt', mode='w', encoding='utf-8')
    for s in corpus:
        corpus_writer.write(' '.join(jieba.lcut(s)))
        corpus_writer.write('\n')
    corpus_writer.close()


def append_faq(files: list = None):
    corpus = get_corpus_from_chat(files)

    question_writer = open(CORPUS_PATH + 'chat_model.question', mode='w', encoding='utf-8')
    answer_writer = open(CORPUS_PATH + 'chat_model.answer', mode='w', encoding='utf-8')
    for i in range(len(corpus) - 1):
        question_writer.write(corpus[i] + '\n')
        answer_writer.write(corpus[i + 1] + '\n')
    question_writer.close()
    answer_writer.close()
    return


def gen_wordcloud():
    corpus = get_corpus_from_chat(['20211203-133402.chat'])
    temp = []
    for txt in corpus:
        txt = jieba.lcut(txt)
        txt = [i for i in txt if len(i) > 1]
        temp.append(' '.join(txt))
    text = ' '.join(temp)
    w = wordcloud.WordCloud(font_path='C:\\WINDOWS\\Fonts\\simfang.ttf', background_color='white', scale=1.5
                            , width=800, height=600)
    w.generate(text)
    w.to_file(os.getcwd() + '\\Img\\wordcloud.png')
    return


def gen_faq_from_record_file(file: list = None):
    corpus = get_corpus_from_chat(file, True)

    # corpus = list(filter(lambda x: re.match(r'^\d{4}-\d{2}-\d{2} \d*:\d*:\d*', x), corpus))
    temp = []
    for c in corpus:
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d*:\d*:\d*', c):
            c = re.sub(r'\[图片\]', '', c)
            c = re.sub(r'\[表情\]', '', c)
            c = re.sub(r'@.+\s', '', c)
            c = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', c)
            if len(c):
                temp.append(c)
    corpus = temp
    del temp
    question_writer = open(CORPUS_PATH + 'chat_model.question', mode='w', encoding='utf-8')
    answer_writer = open(CORPUS_PATH + 'chat_model.answer', mode='w', encoding='utf-8')
    for i in range(len(corpus) - 1):
        question_writer.write(corpus[i] + '\n')
        answer_writer.write(corpus[i + 1] + '\n')
    question_writer.close()
    answer_writer.close()
    return


if __name__ == '__main__':
    gen_faq_from_record_file(['ANS_chat_record.txt'])

pass
