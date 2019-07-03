# 导入requests网络请求模块
import requests
# 导入lxml标签匹配模块
from lxml import etree
# 导入re 正则匹配模块
import re
#导入系统路径模块
import os
# 导入进程模块
import multiprocessing
import threading

# 创建爬虫类
class WangyiMusic(object):
    #创建请求方法 参数为要爬取的网址
    def data_content(self,url):
        #发送request请求获取网页源码  并加入请求头
        data = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
        print(data.text)
        #返回二进制数据
        return data.content
    #写入文件方法  方便数据清洗
    def With(self):
        # 调用请求方法 传入网址参数
        res = self.data_content('https://music.163.com/discover/toplist?id=3778678')
        # 获取源码转车utf-8编码类型 因为网易云音乐为utf-8
        res = res.decode('utf-8') 
        # 写入文件 open打开文件 第一个参数为路径和文件名 第二个参数为写入权限 第三个参数再次声明编码urt-8  as其别名
        with open('./index.html','w',encoding='utf-8') as f:
            # 写入
            f.write(res)
    # 数据清洗
    def Re(self):
        # 读取数据  第一个参数为路径和文件名 第二个参数为读取权限 第三个参数再次声明编码urt-8  as其别名
        with open('./index.html','r',encoding='utf-8') as f:
            # 遍历接收读取数据
            html = f.read()
        #正则匹配想要的数据
        res = re.findall('<li><a href="/song\?id=(.+?)">(.+?)</a></li>',html)
        #定义列表用于存储url
        my_list = []
        #定义列表用于存储歌曲名称
        my_list_name = []
        for i in res:
            #因为网易云音乐的音乐源在 http://music.163.com/song/media/outer/url?id=歌曲id  内所以我们只要获取id即可 这里是拼接歌曲源网址
            my_list.append("http://music.163.com/song/media/outer/url?id="+i[0]+".mp3")
            #取歌曲名加入列表
            my_list_name.append(i[1])
        # 返回参数
        return my_list,my_list_name
    #爬取音乐方法
    def XiaZai(self, url, name):
        # 调用方法发送请求 接收返回数据
        data = self.data_content(url)
        # 写入文件 open打开文件 第一个参数为路径和文件名 第二个参数为写入权限二级制数据 第三个参数再次声明编码urt-8  as其别名
        with open('E:/网易云top200/'+name+'.mp3','wb') as f:
            #写入
            f.write(data)

#程序入库
if __name__ == '__main__':
    # 实例化对象
    wang = WangyiMusic()
    # 调用爬取网址页面并写入文件方法
    wang.With()
    # 调用数据清洗方法 接收参数
    url_list,name_list = wang.Re()
    # 循环 次数为音乐网址的个数
    for i in range(len(url_list)):
        # 调用线程 给予方法 给予参数
        t = threading.Thread(target=wang.XiaZai,args=(url_list[i],name_list[i]))
        #启动线程
        t.start()
    #守护子线程 让主线程等待所以子线程完成后在结束
    t.join()