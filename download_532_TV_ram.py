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
190713����
1��ʹ��tqdm������
2��������������
3������ѡ������
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
from multiprocessing import Pool
# import tqdm
from tqdm import *

# ��Ӱ���Ŀ¼
root_path = os.getcwd()+'\\'
# movie_path = root_path+'movie\\'



def get_all_movie_url():
    #�Զ����ɵ�Ӱ���µ�����ҳ��ÿҳ����30����Ӱ
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


def search_page(keyword,page):
    page = page + 1
    search_url = 'http://532movie.bnu.edu.cn/video/search/wd/' + keyword + '/p/' + str(page) + '.html'
    # print(search_url)
    req = urllib2.Request(search_url)
    response = urllib2.urlopen(req)
    html = response.read()
    movies = re.findall('<a href="/movie/.*?.html" target=', html)
    code_list = []
    for i in movies:
        code = i.split('/')[-1].split('.')[0]
        code_list.append(code)
    return code_list

def search(keyword):
    page = 1
    search_url = 'http://532movie.bnu.edu.cn/video/search/wd/'+keyword+'/p/'+str(page)+'.html'
    req = urllib2.Request(search_url)
    response = urllib2.urlopen(req)
    html = response.read()

    total = re.findall('<br/><div class="page">.*?.&nbsp', html)
    num_char = []
    for num in range(10):
        num_char.append(str(num))

    total_num = []
    for i in total:
        for j in i:
            if j in num_char:
                total_num.append(j)
    # print(total_num)
    if len(total_num) == 0:
        total_page = 1
    else:
        total_num = int(''.join(total_num))
        total_page = total_num/10+1

    range_totala_page = range(total_page)
    arg = []
    for i in range(len(range_totala_page)):
        arg.append([keyword,range_totala_page[i]])

    allcode = []
    flag = 0
    for i in arg:
        flag += 1
        print('searching page %s/%s'%(flag,len(arg)))
        codes = search_page(i[0],i[1])
        for c in codes:
            if c not in allcode:
                allcode.append(c)
            else:
                pass
    dic = {}
    for code in allcode:
        url = 'http://532movie.bnu.edu.cn/player/'+code+'-1.html'
        # all_url.append(url)
        movie_name,_ = get_vedio_url(url)
        dic[movie_name] = url

    return dic



def get_vedio_url(url):
    '''
    ͨ������ƥ��ץȡ��Ƶ����ʵ���ص�ַ�б�
    :param url: ��Ӱ���ŵ�ַ�����磺http://532movie.bnu.edu.cn/player/3379.html
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



def download_movies(url,movie_path,selected_episodes = range(1,int(1e5))):
    '''
    :param url: 'http://532movie.bnu.edu.cn/player/3379.html'
    :return: None
    download *.ts to RAM
    write mp4 movie file to local disk from RAM
    '''
    movie_name, urls = get_vedio_url(url)
    invalid_char = '/\:*"<>|?'
    for ic in invalid_char:
        if ic in movie_name:
            movie_name = movie_name.replace(ic, '.')
    print(movie_name)

    movie_name_utf8 = movie_name.decode('utf-8')
    episode = 0
    flag = 0
    time_init = time.time()
    for i in urls:
        time_start = time.time()
        if len(urls)==1:
            if os.path.isfile(movie_path + movie_name_utf8 + '.mp4'):
                print(movie_path + movie_name_utf8 + '.mp4 is already existed')
                return None
            ts = split_videos(i)

            pool = ThreadPool(20)
            bar_fmt = 'Downloading\t' + '|{bar}|{percentage:3.0f}%'
            results = list(tqdm(pool.imap(download_ts, ts), total=len(ts), ncols=50, bar_format=bar_fmt))
            pool.close()
            pool.join()
            # print('Writing to disk...')
            movie = codecs.open(movie_path+movie_name_utf8+'.mp4', 'wb')
            bar_fmt1 = 'writing to disk\t' + '|{bar}|{percentage:3.0f}%'
            for i in tqdm(range(len(results)),bar_format=bar_fmt1, ncols=50):
                movie.write(results[i])
            movie.close()

        else:
            episode += 1
            if episode not in selected_episodes:
                continue
            TV_dir = movie_path + movie_name_utf8 + '\\'
            if not os.path.isdir(TV_dir):
                os.makedirs(TV_dir)
            if os.path.isfile(TV_dir + 'Episode ' + '%02d' % episode + '.mp4'):
                print(TV_dir + 'Episode ' + '%02d' % episode + '.mp4 is already existed')
                flag += 1
                continue
            pool = ThreadPool(20)
            ts = split_videos(i)
            bar_fmt = 'Episode %02d'%episode+'|{bar}|{percentage:3.0f}%'
            results = list(tqdm(pool.imap(download_ts, ts),total=len(ts),ncols=50,bar_format=bar_fmt))
            pool.close()
            pool.join()

            movie = codecs.open(TV_dir+'Episode '+ '%02d'%episode+'.mp4','wb')
            for r in results:
                movie.write(r)
            time_end = time.time()
            lenurl = len(urls)
            len_selected = len(selected_episodes)
            length = min([lenurl,len_selected])
            log_process.process_bar(flag,length,time_init,time_start,time_end,movie_name+'\n')
            flag += 1



def down_from_text():
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


def main():
    # url = 'http://532movie.bnu.edu.cn/movie/3981.html'
    url = 'http://532movie.bnu.edu.cn/movie/3968.html'
    movie_path = 'C:\\Users\\ly\\Downloads\\Video\\'
    selected = [40,41]
    download_movies(url, movie_path,selected)


if __name__ == '__main__':
    all_url = search(u'��ѩ��'.encode('utf-8'))
    for i in all_url:
        print(i)
        print(all_url[i])
    print(len(all_url))