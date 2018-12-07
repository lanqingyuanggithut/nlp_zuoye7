# -*- coding: utf-8 -*-
import math
import os
import jieba
import re
from scipy.misc import imread  #这是一个处理图像的函数
from wordcloud import WordCloud,ImageColorGenerator
import matplotlib.pyplot as plt
import codecs

def get_idf(word, corpus_list):
    """
    计算idf值
    :param word: 要计算的词
    :param corpus_list: 包含所有语料的list，一个文件为其中一个元素,形式为[[],[],[],·····]
    :return idf: 返回要计算的词的idf值
    """
    num_corpus = len(corpus_list)#语料库的文档总数
    count = 0
    for cur_corpus in corpus_list:
        if word in set(cur_corpus):
            count += 1#count为包含该词的文档数
    idf = math.log(float(num_corpus / (count + 1)))#idf = log(语料库的文档总数 / (包含该词w的文档数 + 1)) 该公式中+1是为了防止分母为0
    return idf


def get_files(path):
    """
    返回所有语料库的文档名字列表
    :param path: 语料库路径
    :return files_list: 返回所有语料库的文档名字列表
    """
    files_list = os.listdir(path)
    return files_list

def get_jieba_wordlist(path_filename):
    """
    输入当前文档，返回该文档的分词列表，分词列表去除所有特殊字符和英文数字
    :param path_filename:
    :return words: 返回该文档的分词结果列表
    """
    with open(path_filename,"r",encoding="utf-8") as f:
        text=f.read()
    r1 = u'[ a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\n]+'
    wordList = jieba.lcut(text)#jieba精确分词,返回列表
    words = []
    for word in wordList:#去除所有特殊字符和英文数字
        word = re.sub(r1, "", word)
        if word != "":
            words.append(word)
    return words#返回分词结果列表

def get_corpus(path):
    """
    获得路径下的所有文本的list，每个文本按空格分为list，形式为[[],[],[],·····]
    :param path: 语料路径（所有文档存放路径）
    :return corpus_list: 语料
    """
    corpus_list = []
    files_list = get_files(path)#获取文件目录，返回文件名list
    for cur_filename in files_list:
        path_filename = path + "/" + cur_filename
        cur_file_words = get_jieba_wordlist(path_filename)
        corpus_list.append(cur_file_words)
    return corpus_list


def save_to_file(path,filename, corpus_list):
    """
    把当前文档的所有关键词以及关键词在语料库中的idf值写入txt文件，txt文件格式为：每个关键词一行，每行的格式为：词 idf值
    :param path: 路径
    :param filename: 文件名
    :param corpus_list: 语料
    :return idf_file:关键词及对应的文件名
    """
    path_filename=os.path.join(path,filename)
    words=list(set(get_jieba_wordlist(path_filename)))
    idf_file="idf"+filename
    f=open(idf_file,"w",encoding="utf-8")
    for word in words:
        idf=get_idf(word, corpus_list)#计算每个词的idf值
        f.write(word+" "+str(idf)+"\n")
    f.close()
    return idf_file

def generate_from_idf_freq(filename):
    """
    根据词的idf值来画词云
    :param path_filename: 存着词和idf值的文档
    :return:无返回值
    """
    back_color = imread('jpg/李白.jpg')  # 解析该图片
    wc = WordCloud(background_color='white',  # 背景颜色
                   max_words=100,  # 最大词数
                   mask=back_color,  #以该参数值作图绘制词云，这个参数不为空时，width和height会被忽略
                   max_font_size=100,  # 显示字体的最大值
                   font_path="C:/Windows/Fonts/simhei.ttf",  #解决显示口字型乱码问题，字体路径C:/Windows/Fonts/
                   random_state=42,  # 为每个词返回一个PIL颜色
                   #width=1000,  # 图片的宽
                   #height=860  # 图片的长
                   )

    # 添加自己的词库分词，比如添加'李世民'到jieba词库后，当你处理的文本中含有李世民这个词，
    # 就会直接将'李世民'当作一个词，而不会得到'李世'或'世民'这样的词
    jieba.add_word('李世民')
    # 打开词源的文本文件
    f = codecs.open(filename, "r", encoding="utf-8")
    lines = f.readlines()
    f.close()

    txt_freq = {}
    for line in lines:
        l = line.split(' ')
        k = l[0]
        v = float(l[1])
        txt_freq[k] = v

    wc.generate_from_frequencies(txt_freq)  # 根据词频生产词云
    # 传入的参数txt_freq是一个字典的形式，例子为
    # {'飘云': 1.252762968495368,'日宇': 1.252762968495368,'李世民':-0.13353139262452263}

    # 基于彩色图像生成相应彩色
    image_colors = ImageColorGenerator(back_color)
    # 显示图片
    plt.imshow(wc)
    # 关闭坐标轴
    plt.axis('off')
    # 绘制词云
    plt.figure()
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')
    # 保存图片
    jpgName=filename[:-4]+".png"
    wc.to_file(jpgName)
    plt.show()

if __name__=="__main__":
    path="txt\\"
    filename="24.txt"
    corpus_list=get_corpus(path)
    idf_file=save_to_file(path,filename,corpus_list)
    generate_from_idf_freq(idf_file)