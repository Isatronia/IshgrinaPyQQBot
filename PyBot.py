from AppiumQQBot import PyBot, log, print_stack_trace
from replyMessage import Prc


def main():
    # bot_inst = PyBot(caps=PyBot.desired_caps_Simulator)
    bot_inst = PyBot(caps=PyBot.desired_caps_Real)
    bot_inst.add_control_flag('record_chat')
    bot_inst.add_control_flag('allow_exec')
    # bot_inst.add_control_flag('no_chat')
    bot_inst.messageProc = Prc()
    bot_inst.readInfoDelay = 1
    bot_inst.set_bot_name('澪依')
    # bot_inst.runEnvironment = 'Dev'
    try:
        bot_inst.run()
    except KeyboardInterrupt:
        log('Bot stop.', PyBot.INFO)
        bot_inst.close()
        return
    except PyBot.TargetGroupImageNotFoundError as e:
        bot_inst.capture_group_image()
        log('Seems that you have not captured group Image, I have captured that for you, see them in folder.')
        bot_inst.close()
        return
    except Exception as e:
        log(e)
        print_stack_trace()
        log('Fatal Error Occured! Bot Kill.')
        bot_inst.close()
        return


if __name__ == "__main__":
    main()
