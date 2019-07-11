# coding=gbk

'''
author: LiYang
date: 20180405
location: BNU Beijing
description: ����532��Ƶ��
�˽ű���������ѧϰ���о�֮�ã���ֹ�Ƿ�������������ҵ��;��������һ�з��������뱾���޹�
190412����
�滻invalid_char = '/\:*"<>|?'
���¶��߳�����
190711����
1���ı����ز��ԣ���*.ts�ļ���д���ڴ棬�ٴ������
2��ʹ��pool �� map���ܲ�������
3����codecs��д�ļ���������gbk��utf-8ת��
'''

import urllib2
import requests
import os
import re
import codecs
import time
import threading
import sys
from multiprocessing.dummy import Pool as ThreadPool

# ��Ӱ���Ŀ¼
root_path = os.getcwd()+'\\'
# movie_path = root_path+'movie\\'


def get_vedio_url(url):
    '''
    ͨ������ƥ��ץȡ��Ƶ����ʵ���ص�ַ�б�
    :param url: ��Ӱ���ŵ�ַ�����磺http://532movie.bnu.edu.cn/player/3379-1.html
    :return: ������Ƶ��ʵ���ص�ַ�б�
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
    movie_name = movie_name.replace(u'<title>���ڲ��� '.encode('utf-8'),'')
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
    ������Ƶ���ָ�ɺܶ�ݣ�һ���������ٶȱȽ�������Ҫ���в�������
    :param split_num: ��������ÿ�ݵ���Ƶ����
    :param url: ��Ƶ����ʵ���ص�ַ
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
    ������Ƶ
    ��������100��ʧ�ܺ󣬽���
    :param video_urls: ��Ƶ��ʵ���ص�ַ
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
            print 'retry times ',attempts
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
    # print(movie_name)
    # print(movie_path)

    movie_name_utf8 = movie_name.decode('utf-8')
    if os.path.isfile(movie_path+movie_name_utf8+'.mp4'):
        # print(movie_name.encode('gbk'))
        # print('.mp4 is existed')
        return None
    # print('downloading ',movie_name)
    # dirname = movie_name
    # exit()

    # dirname = dirname.encode('gbk')

    # open('C:\\Users\\ly\\PycharmProjects\\download_532\\movie\\'+movie_name, 'wb')
    # print(movie_name)
    # codecs.open(movie_path+movie_name, 'wb',encoding='gbk')
    # codecs.open(movie_path + movie_name + '.mp4', 'wb')
    # exit()
    for i in urls:
        pool = ThreadPool(10)
        ts = split_videos(i)
        results = pool.map(download_ts,ts)
        # results = pool.map(download_videos_get_fname,ts)
        pool.close()
        pool.join()
        # print(results)
        movie = codecs.open(movie_path+movie_name_utf8+'.mp4', 'wb')
        for r in results:
            movie.write(r)
        movie.close()


def main():
    movie_path = 'E:\\532_all_movie\\movie\\'
    if not os.path.isdir(movie_path):
        os.makedirs(movie_path)
    f = open('movies_url_list.txt', 'r')
    lines = f.readlines()
    f.close()
    import log_process
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