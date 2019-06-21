# coding=utf-8

'''
author: LiYang
date: 20180405
location: BNU Beijing
description: 下载532视频。
此脚本仅供个人学习、研究之用，禁止非法传播或用于商业用途，若出现一切法律问题与本人无关
'''

import urllib2
import requests
import os
import re
import time
import threading
import sys

# 参数设置
# movie_code = sys.argv[1] # 电影代码
# 例如：
movie_url = sys.argv[1]
root_path = os.getcwd().replace('/','\\')+'\\'
video_temp_path = os.getcwd().replace('/','\\')+'\\python_video_download_temp\\'

print(root_path)

video_temp_path1 = video_temp_path+'temp_movie\\'
# 电影存放目录
movie_path = root_path+'\\movie\\'
# print(video_temp_path1)
# print(movie_path)
# exit()
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
    movie_name = movie_name.replace('/','.')
    movie_name = movie_name.replace(' ','_')
    print movie_name.decode('utf-8').encode('gbk')
    # exit()
    # print movie_name
    # exit()
    urls = []
    for i in url1:
        urls.append(http+i)
    if len(urls) == 0:
        print 'invalid url'
        exit()
    return movie_name,urls


def split_videos(split_num,url):
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
    movies_split = []
    for i in range(len(all_movies)/split_num):
        movies_split.append(all_movies[i*split_num:(i+1)*split_num])
    tail = len(all_movies)-len(movies_split)*split_num
    movies_split.append(all_movies[-tail:])
    return movies_split


def download_videos(video_urls):
    '''
    下载视频
    :param video_urls: 视频真实下载地址
    :return: None
    '''
    for line in video_urls:
        video_i = requests.get(line)
        fname = line.split('/')[-1]
        if os.path.isfile(video_temp_path+fname):
            os.system('del /Q '+video_temp_path+fname)
            exit()
        with open(video_temp_path+fname,'wb') as f:
            f.write(video_i.content)


def concurrent_download(num,url):
    '''
    并行下载
    :param num:  每份下载视频的个数
    :param url:  视频真实下载地址
    :return:  每个Python进程的pid
    '''
    movies_split = split_videos(num,url)
    pids = []
    for i in movies_split:
        # p=Process(target=download_videos,args=(i,))
        # p.start()
        # pids.append(p.pid)
        t = threading.Thread(target=download_videos,args=(i,))
        t.start()


    # for p in pids:
    #     print p
    return pids


def composite_videos(dirname,fname):
    '''
    合成下载的视频
    需要合成两次，一次合成不了那么多视频
    :param dirname:  存储目录
    :param fname:  视频文件名称
    :return:  None
    '''
    f_dir = video_temp_path
    f_list = os.listdir(f_dir)
    shell_str_video_list = []
    for f in f_list:
        if f.endswith('.ts'):
            shell_str_video_list.append(f_dir+f)
    # 第一次合成，每次合成100个文件
    shell_str_video_list_split = []
    for i in range(len(shell_str_video_list)/100):
        shell_str_video_list_split.append(shell_str_video_list[i*100:(i+1)*100])
    tail = len(shell_str_video_list)-len(shell_str_video_list_split)*100
    shell_str_video_list_split.append(shell_str_video_list[-tail:])
    flag = 0
    for shell_split in shell_str_video_list_split:
        flag += 1
        shell_str1 = '+'.join(shell_split)
        shell_str = 'copy /b '+shell_str1+' '+video_temp_path1+'temp_%05d'%flag
        if os.path.isfile(movie_path+'%05d'%flag+'.ts'):
            print 'please rename'
            exit()
        os.system(shell_str+'.ts')
    # 第二次合成
    f1_dir = video_temp_path1
    f1_list = os.listdir(f1_dir)
    shell_str1 = []
    for i in f1_list:
        shell_str1.append(f1_dir+i)
    shell_str1 = '+'.join(shell_str1)
    # dirname = unicode(dirname)
    # print dirname
    # exit()

    # name = name.decode('utf-8')
    # cmd_str = 'md '+name.encode('gbk')
    # os.system(cmd_str)




    shell_str = 'copy /b '+shell_str1+' '+movie_path+dirname+'\\'+dirname+'"'+fname+'"'

    os.system(shell_str+'.ts')


def main():
    os.system('color 17')
    os.system('@echo 版权没有 侵权不究')
    os.system('@echo 此python脚本仅供个人学习、研究之用，禁止非法传播或用于商业用途，若出现一切法律问题与本人无关')
    # os.system('pause')
    # 建立临时文件夹
    if not os.path.isdir(video_temp_path):
        os.mkdir(video_temp_path)
        os.system('attrib +s +h '+video_temp_path[:-1])
    if not os.path.isdir(movie_path):
        os.mkdir(movie_path)
    if not os.path.isdir(video_temp_path1):
        os.mkdir(video_temp_path1)
        os.system('attrib +s +h '+video_temp_path1[:-1])
        # print 'attrib +h '+video_temp_path1[:-1]

    # print 'attrib +s +h '+video_temp_path
    # exit()
    # 删除临时文件夹中的视频文件
    os.system('del /Q '+video_temp_path+'*.ts')
    os.system('del /Q '+video_temp_path1+'*.ts')
    # url='http://532movie.bnu.edu.cn/player/'+str(movie_code)+'.html'
    url = movie_url
    # 获取真实下载地址
    movie_name, download_url = get_vedio_url(url)
    movie_num = len(download_url)

    dirname = movie_name
    dirname = dirname.decode('utf-8')
    dirname = dirname.encode('gbk')

    flag1 = 0
    if not os.path.isdir(movie_path+dirname):
        os.mkdir(movie_path+dirname)

    # 开始下载每个视频
    for i in download_url:
        flag1 += 1
        fname = ' ('+str(flag1)+')'
        # 若发现视频文件已经下载，则跳过下载此视频
        if os.path.isfile(movie_path+dirname+'\\'+dirname+''+fname+'.ts'):
            print (movie_path+dirname+'\\'+dirname+''+fname+'.ts已存在')
            continue

        print i
        # 需要下载的视频数量
        all_num = int(split_videos(10,i)[-1][-1].split('/')[-1].split('.')[0][-7:])
        # 并行下载
        concurrent_download(20,i)
        # 记录进程开始时间
        start = time.time()
        print url
        print fname,'/','%02d'%movie_num
        # download_files_len = 0
        # 监测下载文件数量，每一秒监测一次
        # second = -1
        while 1:
            download_files = os.listdir(video_temp_path)
            # download_files_len1 = len(download_files)
            flag = 0
            # 监测已下载的文件数量
            for f in download_files:
                if f.endswith('.ts'):
                    flag+=1

            # download_files_len = 0+flag
            # print 'timeout',second
            # print '*'*8
            end = time.time()
            breakflag = 0

            # 结束文件数量监测
            if breakflag == 1:
                print 'break'
                break

            print dirname,str(flag1),'%0.3f'%round((float(flag)/all_num*100),3)+'%','\t',int(end-start),'s'
            # 如果下载文件的数量达到需要下载的视频数量则停止监测
            if flag >= all_num:
                break
            # 暂停一秒
            time.sleep(1)
        # 合成下载的视频
        composite_videos(dirname,fname)
        os.system('del /Q '+video_temp_path+'*.ts')
        os.system('del /Q '+video_temp_path1+'*.ts')
        pass
    # 删除临时文件夹
    os.rmdir(video_temp_path1)
    os.rmdir(video_temp_path)


if __name__ == '__main__':
    # get_vedio_url()
    main()
    # url = 'http://532movie.bnu.edu.cn/movie/3488.html'
    # name,urls = get_vedio_url(url)
    # name = name.decode('utf-8')
    # cmd_str = 'md '+name.encode('gbk')
    # os.system(cmd_str)
