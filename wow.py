#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Usage:
        python3
        pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyautogui

        open wow friend panel, screenshots features pictures(eg:好友名单), save to fp.png
        python wow.py
"""


import os
import platform
import time
import random
import pyautogui
import pyperclip
import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug':    logging.DEBUG,
        'info': logging.INFO,
        'warning':  logging.WARNING,
        'error':    logging.ERROR,
    }

    def __init__(self,
                 filename,
                 level='info',
                 when='D',
                 backup_count=3,
                 fmt='%(asctime)s %(name)s %(levelname)s: %(message)s'
                 ):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=backup_count,
            encoding='utf-8'
        )
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


log = Logger('wow.log', level='debug').logger
current_dir = os.path.dirname(os.path.abspath(__file__))


# -------------------------------- config -------------------------------- #

actions_config = {
    "misc": {
        "friend": "o",
        "delay": 10,
        "offline": 10
    },
    "skill": {},
    "move": {},
    "speak": {},
}


def actions_loading():
    global actions_config

    from xml.dom.minidom import parse

    xml_path = os.path.join(current_dir, "actions.xml")
    if not os.path.isfile(xml_path):
        log.error("{} not found!")
        return False

    try:
        dom_tree = parse(xml_path)
        collection = dom_tree.documentElement
        actions = collection.getElementsByTagName("action")
        for action in actions:
            at, ai = action.getAttribute("type"), action.getElementsByTagName('item')
            for item in ai:
                k, v = item.getAttribute("key"), item.childNodes[0].data
                if at not in actions_config:
                    log.warning("{} action not support, ignore!".format(at))
                else:
                    actions_config[at].setdefault(k, v)

        log.debug("user actions config: \n{}".format(actions_config))
        return True

    except Exception as e:
        log.error(e)
        return False

# ------------------------------------------------------------------------ #


class GUI(object):

    gui_ins = None
    delay = 1

    @property
    def gui(self):
        if not self.gui_ins:
            self.gui_ins = pyautogui
            self.gui_ins.PAUSE = self.delay
            self.gui_ins.FAILSAFE = True

        return self.gui_ins

    def tap_once(self, key: str):
        self.gui.press(keys=key)

    def tap_times(self, key: str, rep: int):
        self.gui.press(keys=key, presses=rep)

    def type_string_en(self, value: str):
        self.gui.typewrite(message=value)

    def type_enter(self):
        self.gui.press('enter')

    def type_string_enter(self, value: str):
        self.type_enter()
        pyperclip.copy(value)
        if platform.system() == "Darwin":
            self.gui.hotkey('command', 'v')
        else:
            self.gui.hotkey('ctrl', 'v')
        self.type_enter()

    def locate_image(self, image: str):
        if not os.path.isfile(image):
            log.error("image not found! {}".format(image))
            return None
        try:
            coord = self.gui.locateCenterOnScreen(image)
            return coord
        except Exception as e:
            log.error(e)
            return None

    def alert(self, msg="", title="", timeout=None):
        self.gui.alert(text=msg, title=title, timeout=timeout)

    def left_click(self, x=None, y=None, rep=1):
        self.gui.click(x=x, y=y, clicks=rep)


class Action(GUI):

    name = "action"

    def __init__(self, actions, debug=False):
        self.action = actions.get(self.name)
        self.debug = debug

    def choice(self):
        k = random.choice(list(self.action))
        v = self.action.get(k)
        return k, v

    def call(self):
        k, v = self.choice()
        log.debug("{} {}: {}".format(self.name, k, v))
        if self.debug:
            self.type_string_enter("skill {}.".format(v))
        self.tap_once(k)


class Skill(Action):
    name = "skill"


class Move(Action):
    name = "move"


class Speak(Action):
    name = "speak"

    def call(self):
        k, v = self.choice()
        log.debug("{} {}: {}".format(self.name, k, v))
        if self.debug:
            self.type_string_enter("{}: {}.".format(self.name, v))
        else:
            self.type_string_enter("{}.".format(v))


die_times = 0
misc_friend, misc_delay, misc_offline = "o", 10, 10

RET_EXIT = 1 << 0
RET_SUC = 1 << 1
RET_TRY = 1 << 2


actions_list = [
    Skill, Speak, Move
]


def misc_data_init():
    global misc_friend, misc_delay, misc_offline
    misc_data = actions_config.get("misc")
    misc_friend, misc_delay, misc_offline = \
        misc_data.get("friend", "o"), \
        int(misc_data.get("delay", 10)), \
        int(misc_data.get("offline", 10))


def find_feature_picture(fp_path=None):
    if not fp_path:
        fp_path = os.path.join(current_dir, "fp.png")
    if not os.path.isfile(fp_path):
        log.error("{} is not file!".format(fp_path))
        return False

    coord = GUI().locate_image(fp_path)
    if not coord:
        log.error("Unable to identify {} in WOW! have you open friend panel in WOW?".format(fp_path))
        return False

    log.info("Find picture success! {}".format(coord))

    return coord


def open_fp_panel(key="o"):
    """
        open friends panel, this is used for judge the wow online or not.
    :return:
    """
    GUI().tap_once(key)


def check_online():
    """
        check wow online
    :return:
    """
    global die_times
    if die_times >= misc_offline:
        err = "Check {} times, WOW Not Found in The current screen! will exit.".format(die_times)
        GUI().alert(msg=err, title='Error', timeout=10)
        log.error(err)
        return RET_EXIT

    coord = find_feature_picture()
    if not coord:
        die_times += 1
        open_fp_panel(key=misc_friend)
        return RET_TRY

    GUI().left_click(coord[0], coord[1] + 50, rep=2)
    return RET_SUC


def wow_trusteeship():
    GUI().alert(msg='Make sure that WOW in foreground!', title='Note')
    # GUI().left_click(rep=2)

    if not find_feature_picture():
        return False

    if not actions_loading():
        return False

    misc_data_init()

    while True:
        ret = check_online()

        if ret == RET_EXIT:
            break

        if ret == RET_SUC:
            wf = random.choice(actions_list)(actions=actions_config, debug=False)
            wf.call()

        rt = misc_delay+random.randint(0, 50)
        log.debug("action sleep {}".format(rt))
        time.sleep(rt)


def main():
    wow_trusteeship()

    os.system("pause")


if __name__ == '__main__':
    main()
