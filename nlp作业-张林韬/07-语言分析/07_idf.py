#!usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Edward Amons'


import os
from collections import Counter
import threading
import re
from math import log
import string

import jieba
from wordcloud import WordCloud


def get_files(dirpath):
    """return a file_list"""
    return [x for x in os.listdir(dirpath) if x.endswith('.txt')]


def count_words(filepath):
    """内容分词,同一个词在一片文章内出现多次只记做一次"""

    # 读取文件内容，去除标点
    f = open(filepath, 'r')
    content = ''
    for line in f:
        content += line.split(':')[1].strip()
    CPunc = ' ·！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.'
    content = re.sub('[%s]+' % CPunc, ' ', content)
    content = re.sub('[%s]+' % string.punctuation, ' ', content)
    content = content.strip()
    f.close()

    # 分词
    counter = Counter(set(jieba.cut(content)))
    return counter


def multi_worker(filepath):
    """多线程工人，将文件分词并更新到总计数器中"""
    global words_counter
    counter = count_words(filepath)
    words_counter.update(counter) 


def idf_to_txt(words_idf, filepath):
    """将某文件内的分词idf值写入txt文件"""
    save_dir = os.path.join(os.getcwd(), 'idf_out')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    words = count_words(filepath)
    file_name = os.path.split(filepath)[1]
    outfile_path = os.path.join(save_dir, 'idf_%s' % file_name)
    with open(outfile_path, 'w') as f:
        for word in words.keys():
            f.write('{} {}\n'.format(word, words_idf.get(word)))


def main(dirpath, filename):
    """选择文件夹和其中的一个文件，生成该文件内分词的idf"""
    # import files
    dir_path = os.path.join(os.getcwd(), dirpath)
    file_list = get_files(dir_path)

    # Counter
    global words_counter
    words_counter = Counter()
   
    # multi worker
    for file_name in file_list:
        filepath = os.path.join(dir_path, file_name)
        t = threading.Thread(target=multi_worker, args=(filepath,))
        t.start()

    # counter into dict
    totol_file_number = len(file_list) 
    words_idf = {key: log(totol_file_number/(value+1)) for key, value in words_counter.items()}

    # out file
    file_path = os.path.join(dirpath, filename)
    idf_to_txt(words_idf, file_path)


def ciyun_shiren(dirpath, pic_name):
    """选择文件夹，生成文件夹内分词的词云图，并生成pic_name的图片"""
    # import files
    dir_path = os.path.join(os.getcwd(), dirpath)
    file_list = get_files(dir_path)
    print(dir_path, file_list)

    # Counter
    global words_counter
    words_counter = Counter()
   
    # multi worker
    for file_name in file_list:
        filepath = os.path.join(dir_path, file_name)
        t = threading.Thread(target=multi_worker, args=(filepath,))
        t.start()

    # counter into dict
    print(words_counter)
    # totol_file_number = len(file_list) 
    # words_idf = {key: log(totol_file_number/(value+1)) for key, value in words_counter.items()}

    # dict to wordcloud
    wc = WordCloud(font_path='wqy-zenhei.ttc').generate_from_frequencies(words_counter)
    wc.to_file(pic_name)


if __name__ == '__main__':
    # # test of count_words
    # sc = Counter()
    # count_words('1.txt', sc)
    # print(sc)
    
    # # 某文档内单词的idf计算 
    # main('22', '2.txt')

    # # 某诗人的词云分析 
    ciyun_shiren('libai', 'libai.png')
