# coding=gbk

'''
author: LiYang
date: 20180405
location: BNU Beijing
description: 下载532视频。
此脚本仅供个人学习、研究之用，禁止非法传播或用于商业用途，若出现一切法律问题与本人无关
190412更新
替换invalid_char = '/\:*"<>|?'
更新多线程下载
190711更新
1、改变下载策略，将*.ts文件先写入内存，再存入磁盘
2、使用pool 和 map功能并行下载
3、用codecs库写文件名，不用gbk和utf-8转换
'''

import urllib2
import requests
import os
import re
import codecs
import time
import threading
import sys
import log_process
from multiprocessing.dummy import Pool as ThreadPool

# 电影存放目录
root_path = os.getcwd()+'\\'
# movie_path = root_path+'movie\\'



def get_all_movie_url():
    #自动生成电影栏下的所有页，每页包含30部电影
    page = range(1,38)
    # url_ = 'http://532movie.bnu.edu.cn/list/1/p/'
    url_ = 'http://532movie.bnu.edu.cn/list/2/p/'
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

    fw = open('TV_url_list.txt','w')
    for code in movie_code_list:
        movie_url = 'http://532movie.bnu.edu.cn/movie/%s.html'%code
        print(movie_url)
        fw.write(movie_url+'\n')
    fw.close()



def get_vedio_url(url):
    '''
    通过正则匹配抓取视频的真实下载地址列表
    :param url: 电影播放地址，例如：http://532movie.bnu.edu.cn/player/3379-1.html
    :return: 返回视频真实下载地址列表
    '''
    url_new = url.split('/')
    url_new[-2] = 'player'
    url_new = '/'.join(url_new)
    url = url_new
    req=urllib2.Request(url)
    response=urllib2.urlopen(req)
    html=response.read()
    p=re.findall('playlist.*?;',html)
    for i in p:
        if 'm3u8' in i:
            i = i.split('"')
            url1 = i[1].split('+++')


    p1=re.findall("array.*?;",html)
    for i in p1:
        if 'UrlList' in i:
            i = i.split('"')
            http = i[1]


    p2 = re.findall("<title>.*?</title>",html)

    movie_name = p2[0]
    movie_name = movie_name.replace(u'<title>正在播放 '.encode('utf-8'),'')
    # print movie_name
    movie_name = movie_name.replace('  532movie</title>','')
    movie_name = movie_name.replace('/',' ')
    # movie_name = movie_name.replace(' ','_')

    # exit()
    # try:
        # movie_name.decode('utf-8').encode('gbk')
        # pass
    # except:
        # movie_name = movie_name.split('.')
        # print(movie_name[0])
        # print movie_name[0].decode('utf-8')
        # print movie_name[0].decode('utf-8').encode('gbk')
        # movie_name = movie_name[0]


    # print movie_name
    # exit()
    urls = []
    for i in url1:
        urls.append(http+i)
    if len(urls) == 0:
        print 'invalid url'
        os._exit(0)
    return movie_name,urls


def split_videos(url):
    '''
    由于视频被分割成很多份，一个个下载速度比较慢，需要进行并行下载
    :param split_num: 并行下载每份的视频个数
    :param url: 视频的真实下载地址
    :return:
    '''
    # url = 'http://172.16.215.40:5320/uploads/video6/hls/8/1/8/6/818696bdd65915601b6b6f74b5960abc/wl.m3u8'
    req=urllib2.Request(url)
    response=urllib2.urlopen(req)
    html=response.read()
    html = html.split('\n')
    all_movies = []
    for line in html:
        if line.endswith('.ts'):
            all_movies.append(line)

    return all_movies


def download_ts(video_urls):
    '''
    下载视频
    尝试连接100次失败后，结束
    :param video_urls: 视频真实下载地址
    :return: None
    '''
    # print 'downloading '+video_urls
    attempts = 0
    success = False
    line = video_urls
    # for line in video_urls:
    while 1:
        try:
            # raise IOError
            video_i = requests.get(line,timeout=3.)
            success = True
            attempts = 0
            # print attempts
        except:
            attempts += 1
            # video_i = None
            # print 'retry times ',attempts
            video_i = None
            if attempts == 100:
                print 'download failed'
                print 'please check your network connection'
                os._exit(0)
        if success == True:
            break


    # fname = line.split('/')[-1]
    ts = video_i.content
    # return fname,ts
    return ts


def download_movies(url,movie_path):
    '''
    :param url: 'http://532movie.bnu.edu.cn/player/3379.html'
    :return: None
    download *.ts to RAM
    write mp4 movie file to local disk from RAM
    '''
    movie_name, urls = get_vedio_url(url)
    invalid_char = '/\:*"<>|?'
    # print movie_name,'before'
    for ic in invalid_char:
        if ic in movie_name:
            movie_name = movie_name.replace(ic, '.')
    print(movie_name)
    # print(movie_path)

    movie_name_utf8 = movie_name.decode('utf-8')

    # print('downloading ',movie_name)
    # dirname = movie_name
    # exit()

    # dirname = dirname.encode('gbk')

    # open('C:\\Users\\ly\\PycharmProjects\\download_532\\movie\\'+movie_name, 'wb')
    # print(movie_name)
    # codecs.open(movie_path+movie_name, 'wb',encoding='gbk')
    # codecs.open(movie_path + movie_name + '.mp4', 'wb')
    # exit()

    episode = 0
    flag = 0
    time_init = time.time()
    for i in urls:
        time_start = time.time()
        if len(urls)==1:
            if os.path.isfile(movie_path + movie_name_utf8 + '.mp4'):
                print(movie_path + movie_name_utf8 + '.mp4 is already existed')
                return None
            pool = ThreadPool(20)
            ts = split_videos(i)
            results = pool.map(download_ts, ts)
            # results = pool.map(download_videos_get_fname,ts)
            pool.close()
            pool.join()

            movie = codecs.open(movie_path+movie_name_utf8+'.mp4', 'wb')
            for r in results:
                movie.write(r)
            movie.close()
        else:
            episode += 1
            TV_dir = movie_path + movie_name_utf8 + '\\'
            if not os.path.isdir(TV_dir):
                os.makedirs(TV_dir)
            if os.path.isfile(TV_dir + 'Episode ' + '%02d' % episode + '.mp4'):
                print(TV_dir + 'Episode ' + '%02d' % episode + '.mp4 is already existed')
                flag += 1
                continue
            pool = ThreadPool(20)
            ts = split_videos(i)
            results = pool.map(download_ts, ts)
            # results = pool.map(download_videos_get_fname,ts)
            pool.close()
            pool.join()

            movie = codecs.open(TV_dir+'Episode '+ '%02d'%episode+'.mp4','wb')
            for r in results:
                movie.write(r)
        time_end = time.time()
        log_process.process_bar(flag,len(urls),time_init,time_start,time_end,movie_name+'\n')
        flag += 1



def main():
    movie_path = 'E:\\532_all_movie\\TV\\'
    if not os.path.isdir(movie_path):
        os.makedirs(movie_path)
    f = open('TV_url_list.txt', 'r')
    lines = f.readlines()
    f.close()
    lines = lines[::-1]
    flag = 0
    time_init = time.time()
    for line in lines:
        time_start = time.time()
        url = line.split('\n')[0]
        # print(url)
        movie_name, urls = get_vedio_url(url)
        # print(movie_name.decode('utf-8').encode('gbk'))
        download_movies(url,movie_path)
        time_end = time.time()
        log_process.process_bar(flag,len(lines),time_init,time_start,time_end,'\n')
        flag+=1


if __name__ == '__main__':
    main()