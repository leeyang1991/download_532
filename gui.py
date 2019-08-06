# coding=utf-8
import simple_tkinter as sg
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
from matplotlib import pyplot as plt


Font = ('SimHei', 12)

def check_connection():
    url = 'http://532movie.bnu.edu.cn/'
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        # html = response.read()
        return 1
    except:
        return 0

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
    search_url = search_url.encode('utf-8')
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
    search_url = search_url.encode('utf-8')
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



def download_movies(url,movie_path):
    '''
    :param url: 'http://532movie.bnu.edu.cn/player/3379.html'
    :return: None
    download *.ts to RAM
    write mp4 movie file to local disk from RAM
    '''
    temp_file = str(time.time())
    try:
        codecs.open(movie_path + temp_file, 'wb')
    except:
        sg.Popup(u'路径错误', font=Font)
        return None
    os.remove(movie_path + temp_file)
    movie_name, urls = get_vedio_url(url)
    invalid_char = '/\:*"<>|?'
    for ic in invalid_char:
        if ic in movie_name:
            movie_name = movie_name.replace(ic, '.')
    print(movie_name)
    # try:
    #     print(movie_name.decode('utf-8').encode('utf-8','ignore'))
    # except:
    #     print(movie_name.split()[0].decode('utf-8').encode('utf-8','ignore'))
    #
    try:
        movie_name_utf8 = movie_name.decode('utf-8').encode('gbk','ignore')
    except:
        movie_name_utf8 = movie_name.split()[0].decode('utf-8').encode('gbk','ignore')
    episode = 0
    flag = 0
    # time_init = time.time()

        # time_start = time.time()
    if len(urls)==1:
        if os.path.isfile(movie_path + movie_name.decode('utf-8') + '.mp4'):
            # print(movie_path + movie_name_utf8 + '.mp4 is already existed')
            sg.Popup(movie_path + movie_name.decode('utf-8') + u'已存在',font=Font)
            return None
        ts = split_videos(urls[0])

        pool = ThreadPool(20)
        # bar_fmt = 'Downloading\t' + '|{bar}|{percentage:3.0f}%'
        results = list(tqdm_gui(pool.imap(download_ts, ts), total=len(ts)))
        plt.title('asdf')
        pool.close()
        pool.join()
        # print('Writing to disk...')
        movie = codecs.open(movie_path+movie_name_utf8+'.mp4', 'wb')
        bar_fmt1 = 'writing to disk\t' + '|{bar}|{percentage:3.0f}%'
        for i in tqdm(range(len(results)),bar_format=bar_fmt1, ncols=50):
            movie.write(results[i])
        movie.close()

        plt.close()
        sg.Popup(u'下载完成！', title=u'完成', font=Font)


    else:

        # episode_str = raw_input(
        #     'there are %s episodes, please input a series of numbers like this(e.g.:1,10,15 or 1-3,4-10)' % len(urls))


        text = sg.Text(
            u'共有%s集\n请输入集数\n(例如:1,10,15 or 1-3,4-10)\n直接点击下载所有'%len(urls),
            auto_size_text=1,
            font=Font
            )
        layout = [[text],
                   [sg.Input(), sg.OK(u'下载')],

                   ]
        window = sg.Window(u'选择集数').Layout(layout)
        while 1:

            ev, vals = window.Read()
            if ev is None:
                break
            # episodes = episode_str.split(',')
            print(vals)
            # continue
            if len(vals[0])==0:
                selected = range(1, len(urls)+1)
            else:
                episodes = vals[0].split(',')

                selected = []
                fail1 = 0
                try:
                    for e in episodes:
                        if '-' in e:
                            e_split = e.split('-')
                            e_start = e_split[0]
                            e_end = e_split[1]
                            ee = range(int(e_start), int(e_end) + 1)
                            for ei in ee:
                                selected.append(ei)
                        else:
                            selected.append(int(e))
                except:
                    fail1 = 1

                selected.sort()
                for s in selected:
                    if s > len(urls):
                        print('there are no episode %s' % s)
                        fail1 = 1
                    elif s < 1:
                        print('input error...')
                        fail1 = 1
                if fail1 == 1:
                    sg.PopupError(u'输入有误', title=u'错误', font=Font)
                    continue

            # print selected
            # continue
            text2 = sg.Text('')
            layout2 = [
                [text2],
                [sg.ProgressBar(len(selected), orientation='h', size=(20, 20), key='progressbar')],

            ]
            window2 = sg.Window(u'下载进度').Layout(layout2)
            progress_bar = window2.FindElement('progressbar')

            flag1 = 0
            for i in urls:

                ev2, va2 = window2.Read(timeout=0)
                if ev2 is None:
                    break
                # selected_episodes = range(1, int(1e5))
                text2.Update(i)
                episode += 1
                if episode not in selected:
                    continue
                TV_dir = movie_path + movie_name_utf8 + '\\'
                if not os.path.isdir(TV_dir):
                    os.makedirs(TV_dir)
                if os.path.isfile(TV_dir + 'Episode ' + '%02d' % episode + '.mp4'):
                    # print(TV_dir + 'Episode ' + '%02d' % episode + '.mp4 is already existed')
                    flag += 1
                    # continue
                    sg.Popup(movie_name.decode('utf-8') + 'Episode ' + '%02d' % episode + u'已存在', font=Font)
                    continue
                pool = ThreadPool(20)
                ts = split_videos(i)
                bar_fmt = 'Episode %02d'%episode+'|{bar}|{percentage:3.0f}%'
                results = list(tqdm_gui(pool.imap(download_ts, ts),total=len(ts),ncols=50,bar_format=bar_fmt))
                pool.close()
                pool.join()
                plt.close()
                movie = codecs.open(TV_dir+'Episode '+ '%02d'%episode+'.mp4','wb')
                for r in results:
                    movie.write(r)
                progress_bar.UpdateBar(flag1 + 1)
                flag1+=1
                window2.Close()
        # window.Close()







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



    text = sg.Text('请输入视频网址(例如:http://532movie.bnu.edu.cn/movie/3981.html)\n或输入搜索关键词(例如: 周星驰 或 喜剧之王):'.decode('utf-8'),
                   auto_size_text=1,
                   font=Font
                   )
    layout1 = [[text],
              [sg.Input(), sg.OK(u'搜索')],
              ]

    window1 = sg.Window('Download 532 Movies').Layout(layout1)

    # win2_active = 0
    while 1:
        event1, values1 = window1.Read()
        if not check_connection():
            sg.PopupError(u'连接错误\n请检查网络是否能连接 532movie.bnu.edu.cn', title=u'错误', font=Font)
            continue
        if event1 is None:
            break
        print(values1)
        key_word = values1[0]
        if len(key_word) < 2:
            sg.Popup('请多于2个关键词'.decode('utf-8'))
            continue

        if key_word.startswith('http'):
            movie_name, _ = get_vedio_url(key_word)
            movie_name = [movie_name]
            urls = [key_word]
        else:
            movie_name, urls = search(key_word)
        # key_word = key_word.encode('utf-8')
        for i in movie_name:
            print(i)
        movie_dic = {}
        listbox = []
        for i in range(len(movie_name)):
            movie_dic[movie_name[i].decode('utf-8')] = urls[i]
            listbox.append(movie_name[i].decode('utf-8'))

        if len(movie_name) > 0 and not event1 is None:
            # listbox = movie_name
            sg_listbox = sg.Listbox(listbox, size=(50, 10),font=Font)
            text1 = u'%s\n 搜索结果：共有%s条，请选择要下载的影片'%(key_word,len(movie_name))
            if os.path.isfile(os.getcwd()+'\\config.cfg'):
                config_r = open(os.getcwd()+'\\config.cfg','r')
                lines = config_r.readlines()
                param_dic = {}
                for line in lines:
                    line = line.split('\n')
                    para = line[0].split('=')[0]
                    val = line[0].split('=')[1]
                    param_dic[para] = val
                if 'movie_path' in param_dic:
                    sg_input = sg.Input(param_dic['movie_path'])
                else:
                    sg_input = sg.Input('')
            else:
                sg_input = sg.Input('')
            layout2 = [[sg.Text(text1,font=Font)],
                       [sg_listbox, sg.OK(u'下载')],
                       [sg.Text(u'下载路径',font=Font)],
                       [sg_input,sg.FolderBrowse(u'浏览')]
            ]

            window2 = sg.Window(u'搜索结果').Layout(layout2)
            while 1:
                ev2, vals2 = window2.Read()
                if ev2 is None:
                    window2.Close()
                    break
                if len(vals2[0]) == 0:
                    sg.Popup(u'请选择一个电影', title=u'错误', font=Font)
                    continue
                # print(vals2[0][0])
                url = movie_dic[vals2[0][0]]
                # print(url)
                # print(vals2)
                movie_path=vals2[1]
                if len(movie_path) == 0:
                    sg.Popup(u'请输入下载路径',title=u'错误',font=Font)
                    continue
                # print(movie_path)
                config = open(os.getcwd()+'\\config.cfg','w')
                config.write('movie_path='+movie_path+'\n')
                config.close()
                # sg_input.Update(movie_path)
                # movie_path = os.getcwd()+'\\'
                movie_path = movie_path+'/'

                print(movie_path)
                # exit()
                download_movies(url,movie_path)

        else:
            sg.Popup(u'无搜索结果，请检查关键词',title=u'错误',font=Font)

        if event1 is None:
            break


if __name__ == '__main__':

    main()

    # layout = [[sg.Text('Window 1'), ],
    #           [sg.Input(do_not_clear=True)],
    #           [sg.Text('', key='_OUTPUT_')],
    #           [sg.Button('Launch 2'), sg.Button('Exit')]]
    #
    # win1 = sg.Window('Window 1').Layout(layout)
    #
    # win2_active = False
    # while True:
    #     ev1, vals1 = win1.Read(timeout=100)
    #     # win1.FindElement('_OUTPUT_').Update(vals1[0])
    #     if ev1 is None or ev1 == 'Exit':
    #         break
    #
    #     if not win2_active and ev1 == 'Launch 2':
    #         win2_active = True
    #         layout2 = [[sg.Text('Window 2')],
    #                    [sg.Button('Exit')]]
    #
    #         win2 = sg.Window('Window 2').Layout(layout2)
    #
    #     if win2_active:
    #         ev2, vals2 = win2.Read(timeout=100)
    #         if ev2 is None or ev2 == 'Exit':
    #             win2_active = False
    #             win2.Close()