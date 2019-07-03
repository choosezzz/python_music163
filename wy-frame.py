#—*—coding=utf-8
import requests
import sys
import json
import time
from bs4 import BeautifulSoup
url1 = 'http://music.163.com/discover/toplist?id=3778678'#云音乐热歌榜
#UA必須要設置，未设置获取的网页不完整
headers = {  
    'Cookie':'__e_=1515461191756; _ntes_nnid=af802a7dd2cafc9fef605185da6e73fb,1515461190617; _ntes_nuid=af802a7dd2cafc9fef605185da6e73fb; JSESSIONID-WYYY=HMyeRdf98eDm%2Bi%5CRnK9iB%5ChcSODhA%2Bh4jx5t3z20hhwTRsOCWhBS5Cpn%2B5j%5CVfMIu0i4bQY9sky%5CsvMmHhuwud2cDNbFRD%2FHhWHE61VhovnFrKWXfDAp%5CqO%2B6cEc%2B%2BIXGz83mwrGS78Goo%2BWgsyJb37Oaqr0IehSp288xn5DhgC3Cobe%3A1515585307035; _iuqxldmzr_=32; __utma=94650624.61181594.1515583507.1515583507.1515583507.1; __utmc=94650624; __utmz=94650624.1515583507.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=94650624.4.10.1515583507',  
    'Host':'music.163.com',  
    'Refere':'http://music.163.com/',  
    'Upgrade-Insecure-Requests':'1',  
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'  
}  

response = requests.get(url1,headers=headers)
print(response.status_code)

html = response.text
soup = BeautifulSoup(html,'lxml')
update_time = soup.find('span',attrs={'class':'sep s-fc3'}).text
print(update_time)

#找到json数据
textarea = soup.find('textarea').text
print(textarea)
i = 1
contents = json.loads(str(textarea))

#将数据输出到wangyi.log文件中
fo = open('wangyi.log','w')
sys.stdout = fo
for a in range(len(contents)):
    #发行时间
    t1 = time.localtime(contents[a].get('publishTime')/1000)
    t2 = time.strftime("%Y-%m-%d %H:%M:%S",t1)
    #歌曲时长
    t3 = contents[a].get('duration')/1000
    min = str(t3/60)
    sec = str(t3%60)
    if len(sec)<2:
        sec = '0'+str(sec)
    #歌手
    artist = contents[a].get('artists')[0].get('name')
    #歌名
    music_name = contents[a].get('name')
    #专辑
    album = contents[a].get('album').get('name')
    print(i,'.',music_name,u' 播放时长：',min+':'+str(sec)).encode('gbk')
    print(u'歌手：',artist)
    print(u'专辑：',album)
    #其他信息
    if contents[a].get('alias'):
        alias = contents[a].get('alias')[0]
        print(alias)
    print(u'发行时间：',t2)
    i += 1
    print('--------------------------------------------------------------------')