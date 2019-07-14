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
190711更新
1、改变下载策略，将*.ts文件先写入内存，再存入磁盘
2、使用pool 和 map功能并行下载
3、用codecs库写文件名，不用gbk和utf-8转换
190713更新
1、使用tqdm进度条
2、新增搜索功能
3、新增选集功能
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

# 电影存放目录
root_path = os.getcwd()+'\\'
# movie_path = root_path+'movie\\'


def check_connection():
    url = 'http://532movie.bnu.edu.cn/'
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        # html = response.read()
        print('connection success!')
    except:
        print('connecting to http://532movie.bnu.edu.cn/ failed\nplease check you network connection')
        os.system('pause')
        exit()

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


def search_page(keyword,page):
    page = page + 1
    search_url = 'http://532movie.bnu.edu.cn/video/search/wd/' + keyword + '/p/' + str(page) + '.html'
    # print(search_url)
    # search_url = search_url.decode('gbk').decode('utf-8')
    search_url = search_url.decode('gbk','ignore').encode('utf-8')
    # search_url = search_url.encode('utf-8')
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
    search_url = 'http://532movie.bnu.edu.cn/video/search/wd/' + keyword + '/p/' + str(page) + '.html'
    # print(search_url)
    # search_url = search_url.decode('gbk').decode('utf-8')
    search_url = search_url.decode('gbk', 'ignore').encode('utf-8')
    # print(search_url)
    req = urllib2.Request(search_url)
    response = urllib2.urlopen(req)
    html = response.read()
    # print(html)
    total = re.findall('<br/><div class="page">.*?.&nbsp', html)
    num_char = []
    for num in range(10):
        num_char.append(str(num))

    # print(total)
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
    print('searching...')
    for i in tqdm(range(len(arg))):
        flag += 1
        # print(flag,'/',len(arg))
        codes = search_page(arg[i][0],arg[i][1])
        for c in codes:
            if c not in allcode:
                allcode.append(c)
            else:
                pass
    movie_name_list = []
    url_list = []
    flag1 = 0
    for code in tqdm(range(len(allcode))):
        flag1 += 1
        # print(flag1,'/',len(allcode))
        url = 'http://532movie.bnu.edu.cn/player/'+allcode[code]+'.html'
        movie_name,_ = get_vedio_url(url)
        movie_name_list.append(movie_name)
        url_list.append(url)

    return movie_name_list,url_list



def get_vedio_url(url):
    '''
    通过正则匹配抓取视频的真实下载地址列表
    :param url: 电影播放地址，例如:http://532movie.bnu.edu.cn/player/3379.html
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

    ts = video_i.content
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
    try:
        print(movie_name.decode('utf-8').encode('gbk','ignore'))
    except:
        print(movie_name.split()[0].decode('utf-8').encode('gbk','ignore'))

    try:
        movie_name_utf8 = movie_name.decode('utf-8').encode('gbk','ignore')
    except:
        movie_name_utf8 = movie_name.split()[0].decode('utf-8').encode('gbk','ignore')
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
            try:
                name = movie_name.decode('utf-8').encode('gbk','ignore')
            except:
                name = movie_name.split()[0].decode('utf-8').encode('gbk','ignore')
            log_process.process_bar(flag,length,time_init,time_start,time_end,name+'\n')
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
    check_connection()
    while 1:
        # try:
            print('********************')

            movie_path = os.getcwd()+'\\movie\\'
            if not os.path.isdir(movie_path):
                os.mkdir(movie_path)
            print 'default path is:',movie_path
            input_str = raw_input('please input the movie`s url(e.g.:http://532movie.bnu.edu.cn/movie/3981.html)\nor enter a keyword(e.g."周星驰" or "喜剧之王"):'.decode('utf-8').encode('gbk','ignore'))
            if len(input_str) == 0:
                continue
            if input_str.startswith('http'):
                movie_name, urls = get_vedio_url(input_str)
                # print(movie_name.decode('utf-8'))
                try:
                    print(movie_name.decode('utf-8').encode('gbk','ignore'))
                except:
                    print(movie_name.split()[0].decode('utf-8').encode('gbk','ignore'))
                    print(movie_name.split()[0].decode('utf-8').encode('gbk','ignore'))
                    # encode('GBK', 'ignore').decode('GBk')
                y_n = raw_input('yes/no(y/n) or push enter directly:')
                if y_n in ['n','N','no']:
                    continue
                else:
                    pass
                if len(urls)==1:
                    download_movies(input_str, movie_path)
                else:
                    episode_str = raw_input('there are %s episodes, please input a series of numbers like this(e.g.:1,10,15 or 1-3,4-10)'%len(urls))
                    episodes = episode_str.split(',')
                    selected = []
                    for e in episodes:
                        if '-' in e:
                            e_split = e.split('-')
                            e_start = e_split[0]
                            e_end = e_split[1]
                            ee = range(int(e_start),int(e_end)+1)
                            for ei in ee:
                                selected.append(ei)
                        else:

                            selected.append(int(e))

                    selected.sort()
                    fail1 = 0
                    selected.sort()
                    for s in selected:
                        if s > len(urls):
                            print('there are no episode %s' % s)
                            fail1 = 1
                        elif s < 1:
                            print('input error...')
                            fail1 = 1
                    if fail1 == 1:
                        continue
                    download_movies(input_str, movie_path,selected_episodes=selected)

            else:
                movies,urls_ = search(input_str)
                movie_num = len(movies)
                print('here we got %s'%movie_num+' movies')
                for i in range(len(movies)):
                    try:
                        movies[i].decode('utf-8').encode('gbk','ignore')
                        print i+1,'.',movies[i].decode('utf-8').encode('gbk','ignore')
                    except:
                        print i + 1, '.', movies[i].split()[0].decode('utf-8').encode('gbk','ignore')
                    # print(urls_[i])
                if movie_num == 0:
                    raw_input('search failed, examine your input...\npush enter to continue')
                    continue
                num = raw_input('select a number(1-%s):'%movie_num)
                try:
                    num = int(num)
                except:
                    num = None
                    print('input error...')
                    continue
                if num > movie_num or num < 1:
                    print('input error...')
                    continue
                url = urls_[num-1]
                try:
                    print 'start downloading:\n', movies[num-1].decode('utf-8').encode('gbk','ignore')
                except:
                    print 'start downloading:\n', movies[num - 1].split()[0].decode('utf-8').encode('gbk','ignore')
                y_n = raw_input('yes/no(y/n) or push enter directly:')
                if y_n in ['n', 'N', 'no']:
                    continue
                else:
                    pass
                movie_name, urls = get_vedio_url(url)


                if len(urls)==1:
                    download_movies(url, movie_path)
                else:
                    episode_str = raw_input('there are %s episodes, please input a series of numbers like this(e.g.:1,10,15 or 1-3,4-10)'%len(urls))
                    episodes = episode_str.split(',')
                    selected = []
                    fail = 0
                    for e in episodes:
                        try:
                            if '-' in e:
                                e_split = e.split('-')
                                e_start = e_split[0]
                                e_end = e_split[1]
                                ee = range(int(e_start),int(e_end)+1)
                                for ei in ee:
                                    selected.append(ei)
                            else:
                                selected.append(int(e))
                        except:
                            print('input error...')
                            fail = 1
                    if fail:
                        continue

                    fail1 = 0
                    selected.sort()
                    for s in selected:
                        if s > len(urls):
                            print('there are no episode %s' % s)
                            fail1 = 1
                        elif s < 1:
                            print('input error...')
                            fail1 = 1
                    if fail1 == 1:
                        continue

                    download_movies(url, movie_path,selected_episodes=selected)
            raw_input(u'Done！\npush enter to continue...\n********************\n********************')
            os.system('cls')
        # except Exception as e:
        #     print(e)
        #     print(u'input error, retry...')




if __name__ == '__main__':
    main()

