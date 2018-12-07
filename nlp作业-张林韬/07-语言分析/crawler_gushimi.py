#!usr/bin/env python
# -*- coding: utf-8 -*-

# imports
import os
import logging
import logging.handlers

import requests
from bs4 import BeautifulSoup as Bs

# logging
logger = logging.getLogger(__name__)

handler1 = logging.StreamHandler()
handler2 = logging.FileHandler(filename="crawl_gushimi.log")

logger.setLevel(logging.DEBUG)
handler1.setLevel(logging.INFO)
handler2.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)

logger.addHandler(handler1)
logger.addHandler(handler2)


# create fold
def fold_check(fold_name):
    logger.debug('start fold check')
    if not os.path.exists(fold_name):
        os.mkdir(fold_name)
    return os.path.join(os.getcwd(), fold_name)


# crawl html
def crawl_html(url, encoding='utf-8'):
    """
    return html
    """
    logger.debug('start crawl html')
    req = requests.get(url)
    if req.status_code == 200:
        return req.content.decode(encoding)
    else:
        raise Exception('request status_code: %d' % req.status_code)


# parser dumper
def parse_gushi(html):
    soup = Bs(html, 'lxml')
    # info into dict
    structured_info = {}
    structured_info['title'] = soup.find('h2').string 
    structured_info['dynasty'] = soup.find(text='朝代：').next_element.string
    structured_info['author'] = soup.find(text='作者：').next_element.string

    # tag parser
    def tag_class_news_but_no_id(tag):
        return tag.get("class") == ['newstext'] and not tag.has_attr('id')
    soup_tag = soup.find(tag_class_news_but_no_id)
    tags = [x.string for x in soup_tag('a')]
    tags = str(tags).replace(']', '').replace('[', '')
    structured_info['tags'] = tags 

    # find content
    def tag_has_class_and_id(tag):
        return tag.get('class') == ['newstext'] and tag.has_attr('id')
    soup_tag = soup.find(tag_has_class_and_id)
    content_list = soup_tag(['p', 'div'])
    content_str = ''.join([''.join(x.strings) for x in content_list]).replace('\r', '').replace('\n', '')
    structured_info['content'] = content_str
    return structured_info


def parse_shiren(html):
    """解析诗人页面，并返回该诗人所有诗的url的list"""
    soup = Bs(html, 'lxml')
    collections_shiren = soup('div', class_='relevant_news')[0]
    return [tag['href'] for tag in collections_shiren('a') if tag['href'].startswith('/gushi')]
    

def main_crawl_shiren(url, name_shiren):
    # create folder
    dir_path = fold_check(name_shiren)

    # 抓取诗人页面
    html = crawl_html(url)

    # parse_shiren -> list of url
    gushi_of_shiren = parse_shiren(html)

    # 抓取内容
    for url in gushi_of_shiren:
        try:
            url = 'https://www.gushimi.org' + url
            html = crawl_html(url)
    
            info = parse_gushi(html)

            file_name = info['title'] + '.txt'
            file_name = os.path.join(dir_path, file_name)
            with open(file_name, 'w', encoding='utf-8') as fw:
                content = """title: %s\ndynasty: %s\nauthor: %s\ntags: %s\ncontent: %s""" % (info['title'], info['dynasty'], info['author'], info['tags'], info['content'])
                fw.write(content)
        except Exception:
            pass


def main():
    # create fold
    logger.debug('start main')
    dir_path = fold_check('gushimi')
    logger.debug('dir_path: %s' % dir_path)
   
    # deal with htmls
    count = 0
    index = 1
    while True:
        try:
            # crawl html
            logger.debug('-----------------new_round----------------')
            url = 'https://www.gushimi.org/gushi/%d.html' % index
            logger.info('index: %d::%s' % (index, url))
            html = crawl_html(url)
            logger.debug('html:\n %s' % html)
           
            # parser
            logger.debug('start parser')
            info = parse_gushi(html)
            logger.debug('info: %s' % info)

            # dump into file
            file_name = url.split('/')[-1].split('.')[0] + '.txt'
            file_name = os.path.join(dir_path, file_name)
            with open(file_name, 'w', encoding='utf-8') as fw:
                content = """title: %s\ndynasty: %s\nauthor: %s\ntags: %s\ncontent: %s""" % (info['title'], info['dynasty'], info['author'], info['tags'], info['content'])
                fw.write(content)
            count = 0
        except Exception:
            logger.error('index %d error' % index, exc_info=True)
            count += 1
            if count < 100:
                pass
            else:
                print('finished')
                break
        finally:
            index += 1


def test1(index=5000):
    url = 'https://www.gushimi.org/gushi/%d.html' % index
    dir_path = os.getcwd()
    html = crawl_html(url)
    info = parse_gushi(html)
    file_name = url.split('/')[-1].split('.')[0] + '.txt'
    file_name = os.path.join(dir_path, file_name)
    with open(file_name, 'w', encoding='utf-8') as fw:
        content = "title: %s\ndynasty: %s\nauthor: %s\ntag: %s\ncontent: %s" % (info['title'], info['dynasty'], info['author'], info['tags'], info['content'])
        fw.write(content)


if __name__ == '__main__':
    url = 'https://www.gushimi.org/shiren/5.html'
    shiren = 'libai'
    main_crawl_shiren(url, shiren)
    #html = crawl_html(url)
    #parse_shiren(html)
    # test1()
