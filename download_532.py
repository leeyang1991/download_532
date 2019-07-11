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
'''

import urllib2
import requests
import os
import re
import time
import threading
import sys

# ��������
# movie_code = sys.argv[1] # ��Ӱ����
# dirname = sys.argv[2] # ��Ӱ����
# disk = sys.argv[3] # �洢����
# ���磺
# movie_url = sys.argv[1]
movie_url = 'http://532movie.bnu.edu.cn/movie/3738.html'
# disk = 'G'
# ������ʱ����Ŀ¼
# video_temp_path = disk+':\\python_video_download_temp\\'
root_path = os.getcwd().replace('/','\\')+'\\'
video_temp_path = os.getcwd().replace('/','\\')+'\\python_video_download_temp\\'

print(root_path)


# exit()
video_temp_path1 = video_temp_path+'temp_movie\\'
# ��Ӱ���Ŀ¼
movie_path = root_path+'\\movie\\'
# print(video_temp_path1)
# print(movie_path)
# exit()
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
    movie_name = movie_name.replace('/','.')
    movie_name = movie_name.replace(' ','_')

    # exit()
    try:
        print movie_name.decode('utf-8').encode('gbk')

    except:
        movie_name = movie_name.split('.')
        print(movie_name[0])
        # print movie_name[0].decode('utf-8')
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

    # movies_split = []
    # for i in range(len(all_movies)/split_num):
    #     movies_split.append(all_movies[i*split_num:(i+1)*split_num])
    # tail = len(all_movies)-len(movies_split)*split_num
    # movies_split.append(all_movies[-tail:])

    return all_movies


def download_videos(video_urls):
    '''
    ������Ƶ
    ��������10��ʧ�ܺ󣬽���
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
            if attempts == 10:
                print 'download failed'
                print 'please check your network connection'
                os._exit(0)
        if success == True:
            break

    fname = line.split('/')[-1]
    with open(video_temp_path+fname,'wb') as f:
        f.write(video_i.content)
    # print 'done'



def concurrent_download_kernel(video_url):
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
            print 'retry times ', attempts
            if attempts == 10:
                print 'download failed'
                print 'please check your network connection'
                os._exit(0)
        if success == True:
            break

    fname = line.split('/')[-1]
    with open(video_temp_path + fname, 'wb') as f:
        f.write(video_i.content)


def concurrent_download(url,movie_name):
    '''
    ��������
    :param num:  ÿ��������Ƶ�ĸ���
    :param url:  ��Ƶ��ʵ���ص�ַ
    :return:  None
    '''
    # movies_split = split_videos(num,url)
    urls = split_videos(url)
    # print urls
    start = time.time()
    for i in range(len(urls)):
        # print urls[i]
        # exit()
        t = threading.Thread(target=download_videos,args=(urls[i],))
        t.start()
        # t.join()
        # print str(i+1),'/',len(urls)
        if (i+1)%(len(urls)/100) == 0:
            print movie_name,'%02d'%(float(i+1)/len(urls)*100),'%'
        # thread_ = len(threading.enumerate())
        # while 1:
        #     # time.sleep(1)
        #     # ����
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



def composite_videos(dirname,fname):
    '''
    �ϳ����ص���Ƶ
    ��Ҫ�ϳ����Σ�һ�κϳɲ�����ô����Ƶ
    :param dirname:  �洢Ŀ¼
    :param fname:  ��Ƶ�ļ�����
    :return:  None
    '''
    f_dir = video_temp_path
    f_list = os.listdir(f_dir)
    shell_str_video_list = []
    for f in f_list:
        if f.endswith('.ts'):
            shell_str_video_list.append(f_dir+f)
    # ��һ�κϳɣ�ÿ�κϳ�100���ļ�
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
    # �ڶ��κϳ�
    f1_dir = video_temp_path1
    f1_list = os.listdir(f1_dir)
    shell_str1 = []
    for i in f1_list:
        shell_str1.append(f1_dir+i)
    shell_str1 = '+'.join(shell_str1)
    shell_str = 'copy /b '+shell_str1+' '+movie_path+dirname+'\\'+dirname+'"'+fname+'"'

    os.system(shell_str+'.mp4')


def main():
    os.system('color 17')
    # os.system('@echo ��Ȩû�� ��Ȩ����')
    # os.system('@echo ��python�ű���������ѧϰ���о�֮�ã���ֹ�Ƿ�������������ҵ��;��������һ�з��������뱾���޹�')
    # os.system('pause')
    # ������ʱ�ļ���
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
    # ɾ����ʱ�ļ����е���Ƶ�ļ�
    os.system('del /Q '+video_temp_path+'*.ts')
    os.system('del /Q '+video_temp_path1+'*.ts')
    # url='http://532movie.bnu.edu.cn/player/'+str(movie_code)+'.html'
    # url = 'http://532movie.bnu.edu.cn/movie/3676.html'
    url = movie_url
    # ��ȡ��ʵ���ص�ַ
    movie_name, download_url = get_vedio_url(url)
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
    if not os.path.isdir(movie_path+dirname):
        os.mkdir(movie_path+dirname)

    # ��ʼ����ÿ����Ƶ
    for i in download_url:
        flag1 += 1
        fname = ' ('+str(flag1)+')'
        # ��������Ƶ�ļ��Ѿ����أ����������ش���Ƶ
        if os.path.isfile(movie_path+dirname+'\\'+dirname+''+fname+'.mp4'):
            print (movie_path+dirname+'\\'+dirname+''+fname+'.mp4�Ѵ���')
            continue

        print i
        # ��Ҫ���ص���Ƶ����
        # all_num = int(split_videos(10,i)[-1][-1].split('/')[-1].split('.')[0][-7:])
        all_num = len(split_videos(i))
        # ��������
        concurrent_download(i,dirname)
        # ��¼���̿�ʼʱ��
        start = time.time()
        print url
        print fname,'/','%02d'%movie_num
        # download_files_len = 0
        # ��������ļ�������ÿһ����һ��
        # second = -1
        while 1:
            download_files = os.listdir(video_temp_path)
            # download_files_len1 = len(download_files)
            flag = 0
            # ��������ص��ļ�����
            for f in download_files:
                if f.endswith('.ts'):
                    flag+=1

            # download_files_len = 0+flag
            # print 'timeout',second
            # print '*'*8
            end = time.time()
            breakflag = 0

            # �����ļ��������
            if breakflag == 1:
                print 'break'
                break

            print 'checking',str(flag1),'%0.3f'%round((float(flag)/all_num*100),3)+'%','\t',int(end-start),'s'
            # ��������ļ��������ﵽ��Ҫ���ص���Ƶ������ֹͣ���
            if flag >= all_num:
                break
            # ��ͣһ��
            time.sleep(1)
        # �ϳ����ص���Ƶ
        composite_videos(dirname,fname)
        os.system('del /Q '+video_temp_path+'*.ts')
        os.system('del /Q '+video_temp_path1+'*.ts')
        pass
    # ɾ����ʱ�ļ���
    os.rmdir(video_temp_path1)
    os.rmdir(video_temp_path)


if __name__ == '__main__':

    main()
