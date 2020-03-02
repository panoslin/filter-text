#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/2/6
# IDE: PyCharm

__all__ = ['DFAFilter']
__author__ = 'observer'
__date__ = '2012.01.05'

from collections import defaultdict
import re


class Singleton:
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


@Singleton
class BSFilter:
    """Filter Messages from keywords
    Use Back Sorted Mapping to reduce replacement times
    >>> f = BSFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby

    More than 10 times slower than DFAFilter，but can do the job
    """

    def __init__(self):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        try:
            with open(path) as f:
                for keyword in f:
                    self.add(keyword.strip())
        except IsADirectoryError:
            for file in glob(os.path.join(path.rstrip("/"), "*")):
                with open(file) as f:
                    for keyword in f:
                        self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):  ## if is english
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:  ## if is chinese
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message

    def match(self, message):
        if message is None:
            return {}
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        keywords = set()
        for word in message.split():
            if self.pat_en.search(word):  ## if is english
                for index in self.bsdict[word]:
                    if self.keywords[index] in message:
                        keywords.add(self.keywords[index])
            else:  ## if is chinese
                for char in word:
                    for index in self.bsdict[char]:
                        if self.keywords[index] in message:
                            keywords.add(self.keywords[index])
                        # message = message.replace(self.keywords[index], repl)
        return keywords


@Singleton
class DFAFilter:
    """
    Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    """

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        try:
            with open(path) as f:
                for keyword in f:
                    self.add(keyword.strip())
        except IsADirectoryError:
            for file in glob(os.path.join(path.rstrip("/"), "*")):
                with open(file) as f:
                    for keyword in f:
                        self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)

    def match(self, message):
        if message is None:
            return {}
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        start = 0
        keywords = set()
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        keywords.add(message[start: start + step_ins])
                        start += step_ins - 1
                        break
                else:
                    break
            start += 1

        return keywords


# def test_first_character():
#     gfw = DFAFilter()
#     gfw.add("1989年")
#     assert gfw.filter("1989", "*") == "1989"


if __name__ == "__main__":
    # gfw = NaiveFilter()
    # gfw = BSFilter()
    gfw = DFAFilter()
    from glob import glob
    import os
    print(os.path.join(os.getcwd(), "keywords/*"))
    # for keywords_file in glob(os.path.join(os.getcwd(), "keywords/*")):
    gfw.parse(os.path.join(os.getcwd(), "keywords"))

    # print(gfw.filter("法轮功 我操操操", "*"))
    # print(gfw.filter("针孔摄像机 我操操操", "*"))
    # print(gfw.filter("售假人民币 我操操操", "*"))
    # print(gfw.filter("我操作电脑", "*"))
    # print(gfw.filter("class over", "*"))

    print(gfw.match("法轮功 我操操操"))
    print(gfw.match("针孔摄像机 我操操操"))
    print(gfw.match("售假人民币 我操操操"))
    print(gfw.match("我操作电脑"))
    print(gfw.match("class over"))
    print(gfw.match("如果有吃肉欲望"))
    print(gfw.match("8cm肉欲拉面终于来福田了，招牌辣么大"))

    # import time
    # start_ = time.time()
    # for i in range (1, 1000):
    #     print(gfw.match("法轮功 我操操操"))
    #     print(gfw.match("针孔摄像机 我操操操"))
    #     print(gfw.match("售假人民币 我操操操"))
    #     print(gfw.match("我操作电脑"))
    #     print(gfw.match("class over"))
    # print(time.time() - start_)
    # test_first_character()
