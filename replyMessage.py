import random
from typing import Iterable

from corpusGenerator import gen_wordcloud


class Prc:
    def __init__(self) -> None:
        pass

    @staticmethod
    def arg_len_check(args: Iterable, length: int) -> None:
        if len(args) != length:
            raise ValueError('Value Num not fit')
        return

    @staticmethod
    def wordcloud(self):
        gen_wordcloud()
        return u'看看你们都聊了些什么鬼罢。'

    def dice(self, args: Iterable) -> str:
        self.arg_len_check(args, 2)
        args = tuple(map(int, args))
        return str(random.randrange(args[0], args[1]))

    def rd(self, args: Iterable) -> str:
        self.arg_len_check(args, 1)
        args = tuple(map(int, args))
        return str(random.randrange(args[0]))
