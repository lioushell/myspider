#!/usr/bin/env python
# coding=utf-8
import os
import time
import json
import requests
from bs4 import BeautifulSoup
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

url_type = "https://m.ximalaya.com/tracks/%s.json"
HEADERS = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Host': "www.ximalaya.com"
}
PATH = r'D:/audios/'#下载路径
URL_SET = set({})#去重使用，可以用Redis替换


def get_xmly(url_name, url):
    try:
        os.makedirs(PATH + url_name)
    except FileExistsError:
        pass
    s = requests.session()
    r1 = s.get(url=url, headers=HEADERS)
    bs = BeautifulSoup(r1.text, 'html.parser')
    ul = bs.find(name='div', attrs={'class': 'content'})
    li_list = ul.find_all(name='li')
    for li in li_list:
        uid = li.find(name='a').get('href').split('/')[2]
        msg = s.get(url=url_type % uid)
        res = json.loads(msg.text)
        if res.get('res') == None:
            get_audio(res, url_name)
        time.sleep(2)


def get_audio(res, url_name):
    id = res.get('id')
    if id in URL_SET:
        pass
    else:
        URL_SET.add(id)
        play_path_64 = res.get('play_path_64')
        audio_content = requests.get(play_path_64).content
        title = res.get('title')
        cover_url_142 = res.get('cover_url_142')
        filename = (title + '.' + play_path_64.rsplit('.', maxsplit=1)[-1]).replace(' ', '')
        filepath = PATH + url_name + '/' + filename
        with open(filepath, 'wb') as f:
            f.write(audio_content)


if __name__ == '__main__':
    cpu_count = cpu_count()
    p = ThreadPoolExecutor(cpu_count + 1)
    url_dict = {
        'ertongwenxue': 'https://www.ximalaya.com/ertong/ertongwenxue/mr19t10r132t2722/',
        'kepubaike': 'https://www.ximalaya.com/ertong/kepubaike/mr19t10r132t2722/',
        'shaoeryinyue': 'https://www.ximalaya.com/ertong/shaoeryinyue/mr19t10r132t2722/',
        'xueqianyingyu': 'https://www.ximalaya.com/ertong/xueqianyingyu/mr19t10r132t2722/',
        'shaoeryingshi': 'https://www.ximalaya.com/ertong/shaoeryingshi/mr19t10r132t2722/',
    }
    for url_name, url in url_dict.items():
        p.submit(get_xmly, url_name, url)
