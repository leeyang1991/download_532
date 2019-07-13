# coding=utf-8

'''
author: LiYang
date: 20180405
location: BNU Beijing
description: 下载532视频。
此脚本仅供个人学习、研究之用，禁止非法传播或用于商业用途，若出现一切法律问题与本人无关
190412更新
替换invalid_char = '/\:*"<>|?'
更新多线程下载
'''

import urllib2
import requests
import os
import re
import time
import threading
import datetime

##下载路径目录##
# root_path = os.getcwd().replace('/', '\\') + '\\'
root_path = 'F:\\532_all_movie\\'
##下载路径目录##
# video_temp_path = root_path + 'python_video_download_temp\\'
# print(root_path)
# video_temp_path1 = video_temp_path + 'temp_movie\\'
# movie_path = root_path+'\\movie\\'

def get_all_movie_url():
    #自动生成电影栏下的所有页，每页包含30部电影
    page = range(1,58)
    url_ = 'http://532movie.bnu.edu.cn/list/1/p/'
    url_list = []
    for p in page:
        url_list.append(url_+str(p)+'.html')

    movie_code_list = []
    for url in url_list:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        html = response.read()
        p = re.findall('<a target="_blank" href="/movie/.*?.html" class="', html)
        for i in p:
            code = i.split('/')[-1].split('.')[0]
            movie_code_list.append(code)

    fw = open('movies_url_list.txt','w')
    for code in movie_code_list:
        movie_url = 'http://532movie.bnu.edu.cn/movie/%s.html'%code
        print(movie_url)
        fw.write(movie_url+'\n')
    fw.close()


def main():

    get_all_movie_url()


if __name__ == '__main__':
    main()




