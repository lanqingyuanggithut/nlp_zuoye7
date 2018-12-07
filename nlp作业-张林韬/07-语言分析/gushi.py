#/usr/bin/env python
#! -*- coding: utf-8 -*-

__author__ = "Edward Amons"


import re

import jieba

import crawler_gushimi


# class Gushi
class Gushi(object):
    """used to bind data and method of Gushi"""
    def __init__(self, title, **kwargs):
        self._title = title
        self._author = kwargs.get('author')
        self._content = kwargs.get('content')
        self._dynasty = kwargs.get('dynasty')
        self._tags = kwargs.get('tags')

    def __repr__(self):
        return "题目：%s 作者：%s" % (self._title, self._author)

    def __str__(self):
        return "题目：%s 作者：%s" % (self._title, self._author)

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, author):
        self._author = author

    @property
    def dynasty(self) -> str:
        return self._dynasty

    @dynasty.setter
    def dynasty(self, dynasty):
        self._dynasty = dynasty

    @property
    def tags(self) -> list:
        return self._tags

    @tags.setter
    def tags(self, tags):
        self._tags = tags

    def word_segmentation(self):
        """将古诗内容分词，返回分词的集合，重复的词仅计算一次,
        不计算'，', '。'这两个标点符号"""
        s = set(jieba.cut(self.content))
        s.remove('，')
        s.remove('。')
        return s
        
        
def read_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        title = re.match(r'title: (.*)', lines[0]).group(1)
        dynasty = re.match(r'dynasty: (.*)', lines[1]).group(1)
        author = re.match(r'author: (.*)', lines[2]).group(1)
        tags = re.match(r'tags: (.*)', lines[3]).group(1)
        tags = [x.strip("\'") for x in tags.split(', ')]
        content = re.match(r'content: (.*)', lines[4]).group(1)

        return Gushi(title, dynasty=dynasty, author=author, tags=tags, content=content)
        

def from_url(url):
    html = crawler_gushimi.crawl_html(url)
    dict_info = crawler_gushimi.parse_html(html)
    return Gushi(dict_info['title'],
            dynasty=dict_info['dynasty'],
            author=dict_info['author'],
            tags=dict_info['tags'],
            content=dict_info['content'])

        
if __name__ == "__main__":
    # a = read_txt('1.txt')

    # url = 'https://www.gushimi.org/gushi/%d.html' % 1
    # a = from_url(url)
    # print("a.title: ", a.title)
    # print("a.author: ", a.author)
    # print("a.dynasty: ", a.dynasty)
    # print("a.tags: ", a.tags)
    # print("a.content: ", a.content)
    
    a = read_txt('gushimi/1.txt')
    print(a)
    b = a.word_segmentation()
    print(type(b))
