import xlwt
import requests
from bs4 import BeautifulSoup
import re

url = 'http://music.163.com/discover/artist/cat?id=1001'  # 华语男歌手页面
r = requests.get(url)
r.raise_for_status()
r.encoding = r.apparent_encoding
html = r.text  # 获取整个网页
soup = BeautifulSoup(html, 'html.parser')  #
top_10 = soup.find_all('div', attrs={'class': 'u-cover u-cover-5'})
print(top_10)

singers = []
for i in top_10:
    singers.append(re.findall(r'.*?<a class="msk" href="(/artist\?id=\d+)" title="(.*?)的音乐"></a>.*?', str(i))[0])
# print(singers)

url = 'http://music.163.com'
for singer in singers:
    try:
        new_url = url + str(singer[0])
        # print(new_url)
        songs = requests.get(new_url).text
        soup = BeautifulSoup(songs, 'html.parser')
        Info = soup.find_all('textarea', attrs={'style': 'display:none;'})[0]
        songs_url_and_name = soup.find_all('ul', attrs={'class': 'f-hide'})[0]
        # print(songs_url_and_name)
        datas = []
        data1 = re.findall(r'"album".*?"name":"(.*?)".*?', str(Info.text))
        data2 = re.findall(r'.*?<li><a href="(/song\?id=\d+)">(.*?)</a></li>.*?', str(songs_url_and_name))

        for i in range(len(data2)):
            datas.append([data2[i][1], data1[i], 'http://music.163.com/#' + str(data2[i][0])])
        # print(datas)
        book = xlwt.Workbook()
        sheet1 = book.add_sheet('sheet1', cell_overwrite_ok=True)
        sheet1.col(0).width = (25 * 256)
        sheet1.col(1).width = (30 * 256)
        sheet1.col(2).width = (40 * 256)
        heads = ['歌曲名称', '专辑', '歌曲链接']
        count = 0

        for head in heads:
            sheet1.write(0, count, head)
            count += 1

        i = 1
        for data in datas:
            j = 0
            for k in data:
                sheet1.write(i, j, k)
                j += 1
            i += 1
        book.save(str(singer[1]) + '.xls')  # 括号里写存入的地址

    except:
        continue