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

    # exit()
    try:
        print movie_name.decode('utf-8').encode('gbk')

    except:
        movie_name = movie_name.split('.')
        print movie_name[0].decode('utf-8').encode('gbk')
        movie_name = movie_name[0]


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

    # movies_split = []
    # for i in range(len(all_movies)/split_num):
    #     movies_split.append(all_movies[i*split_num:(i+1)*split_num])
    # tail = len(all_movies)-len(movies_split)*split_num
    # movies_split.append(all_movies[-tail:])

    return all_movies


def download_videos(video_urls,video_temp_path):
    '''
    下载视频
    尝试连接10次失败后，结束
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
            time.sleep(1)
            if attempts == 100:
                print 'download failed'
                print 'please check your network connection'
                os._exit(0)
        if success == True:
            break

    fname = line.split('/')[-1]
    with open(video_temp_path+fname,'wb') as f:
        f.write(video_i.content)
    # print 'done'



def concurrent_download_kernel(video_url,video_temp_path):
    attempts = 0
    success = False
    line = video_url
    while 1:
        try:
            # raise IOError
            video_i = requests.get(line)
            success = True
            attempts = 0
            # print attempts
        except:
            attempts += 1
            video_i = None
            print 'retry times ', attempts,'sleep 1 second'
            time.sleep(1)
            if attempts == 100:
                print 'download failed'
                print 'please check your network connection'
                os._exit(0)
        if success == True:
            break

    fname = line.split('/')[-1]
    with open(video_temp_path + fname, 'wb') as f:
        f.write(video_i.content)


def concurrent_download(url,movie_name,video_temp_path):
    '''
    并行下载
    :param num:  每份下载视频的个数
    :param url:  视频真实下载地址
    :return:  None
    '''
    # movies_split = split_videos(num,url)
    urls = split_videos(url)
    # print urls
    start = time.time()
    threads = []
    for i in range(len(urls)):
        # print urls[i]
        # exit()
        t = threading.Thread(target=download_videos,args=(urls[i],video_temp_path,))
        threads.append(t)
    i=0
    for t in threads:
        i += 1
        t.start()
        if (i+1)%(len(urls)/100) == 0:
            print 'initializing',movie_name,'%02d'%(float(i+1)/len(urls)*100),'%'
    return threads
        # thread_ = len(threading.enumerate())
        # while 1:
        #     # time.sleep(1)
        #     # 更新
        #     # python_process = self.count_python_process()
        #     python_process = thread_
        #     if python_process <= num:
        #         break
        #     else:
        #         end = time.time()
        #         # print
        #         # current_files_len = count_files_num()
        #         print int(end - start), 's', '/', 'python_process', python_process
        #         # print('init_files_len',init_files_len)
        #         # print 'looping'
        #         # time.sleep(0.1)



def composite_videos(dirname,fname,video_temp_path,video_temp_path1,movie_path):
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
        os.system(shell_str+'.ts')
    # 第二次合成
    f1_dir = video_temp_path1
    f1_list = os.listdir(f1_dir)
    shell_str1 = []
    for i in f1_list:
        shell_str1.append(f1_dir+i)
    shell_str1 = '+'.join(shell_str1)
    shell_str = 'copy /b '+shell_str1+' '+movie_path+dirname+'\\'+dirname+'"'+fname+'"'

    os.system(shell_str+'.mp4')



def download_all_movie():

    f = open('movies_url_list.txt','r')
    lines = f.readlines()
    f.close()
    for line in lines:
        url = line.split('\n')[0]
        print(url)
        str_date = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        # str_date = datetime.datetime.now()
        # str_date.
        video_temp_path = root_path + 'python_video_download_temp_' + str_date + '\\'
        # print(root_path)
        print(video_temp_path)
        # exit()
        video_temp_path1 = video_temp_path + 'temp_movie\\'
        movie_path = root_path + '\\movie\\'
        # 建立临时文件夹
        if not os.path.isdir(video_temp_path):
            os.mkdir(video_temp_path)
            os.system('attrib +s +h ' + video_temp_path[:-1])
        if not os.path.isdir(movie_path):
            os.mkdir(movie_path)
        if not os.path.isdir(video_temp_path1):
            os.mkdir(video_temp_path1)
            os.system('attrib +s +h ' + video_temp_path1[:-1])
            # print 'attrib +h '+video_temp_path1[:-1]

        # print 'attrib +s +h '+video_temp_path
        # exit()
        # 删除临时文件夹中的视频文件
        # os.system('del /Q ' + video_temp_path + '*.ts')
        # os.system('del /Q ' + video_temp_path1 + '*.ts')
        # url='http://532movie.bnu.edu.cn/player/'+str(movie_code)+'.html'
        # url = 'http://532movie.bnu.edu.cn/movie/3676.html'
        # url = movie_url
        # 获取真实下载地址
        movie_name, download_url = get_vedio_url(url)
        # print(movie_name)
        # exit()
        movie_num = len(download_url)
        invalid_char = '/\:*"<>|?'
        # print movie_name,'before'
        for ic in invalid_char:
            if ic in movie_name:
                movie_name = movie_name.replace(ic, '.')
        # print movie_name,'after'
        # exit()
        dirname = movie_name
        dirname = dirname.decode('utf-8')
        dirname = dirname.encode('gbk')

        flag1 = 0
        if not os.path.isdir(movie_path + dirname):
            os.mkdir(movie_path + dirname)

        # 开始下载每个视频
        for i in download_url:
            flag1 += 1
            fname = ' (' + str(flag1) + ')'
            # 若发现视频文件已经下载，则跳过下载此视频
            if os.path.isfile(movie_path + dirname + '\\' + dirname + '' + fname + '.mp4'):
                print (movie_path + dirname + '\\' + dirname + '' + fname + '.mp4已存在')
                continue

            print i
            # 需要下载的视频数量
            # all_num = int(split_videos(10,i)[-1][-1].split('/')[-1].split('.')[0][-7:])
            all_num = len(split_videos(i))
            # 并行下载
            threads = concurrent_download(i, dirname,video_temp_path)
            # 记录进程开始时间
            start = time.time()
            print url
            print fname, '/', '%02d' % movie_num
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
                        flag += 1

                # download_files_len = 0+flag
                # print 'timeout',second
                # print '*'*8
                end = time.time()
                breakflag = 0

                # 结束文件数量监测
                if breakflag == 1:
                    print 'break'
                    break

                print 'downloading', str(flag1), '%0.3f' % round((float(flag) / all_num * 100), 3) + '%', '\t', int(
                    end - start), 's'
                # 如果下载文件的数量达到需要下载的视频数量则停止监测
                if flag >= all_num:
                    break
                # 暂停一秒
                time.sleep(1)

            print('closing threads')
            for t in threads:
                t.join()

            # 合成下载的视频
            composite_videos(dirname, fname,video_temp_path,video_temp_path1,movie_path)
            # 关闭进程

            # os.system('del /Q ' + video_temp_path + '*.ts')
            # os.system('del /Q ' + video_temp_path1 + '*.ts')
            # pass
        # 删除临时文件夹
        # os.rmdir(video_temp_path1)
        # os.rmdir(video_temp_path)

def main():

    download_all_movie()


if __name__ == '__main__':
    main()




