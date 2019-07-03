import requests
from bs4 import BeautifulSoup
import json
import xlwt
import time
url = "https://music.163.com/discover/toplist?id=3778678"

#添加请求头
headers = {
    'cookie': '_iuqxldmzr_=32; _ntes_nnid=a662d3c2e4f2914fd042904bd19585b0,1562137812793; _ntes_nuid=a662d3c2e4f2914fd042904bd19585b0; WM_NI=fxRIla05f8Trg1PxAyCSnPrigsd87wIi8hdEtx1yN9E3k9R80c4X4XFrwUZxMCTzE2gXGKxpzY6Js7Ae0inmmD9ZQzAtPLoH2hPy5zFT2uAeCW%2BLP2hO4OGtbgxBPb6qRVM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeacb37b9af5e195e66d88a88ab6c85e878f8faeb866adb0c09ae73fb89cbdd8b22af0fea7c3b92aa6a89eaaef6bf4ebaad9d77aa5efa099c473818da2b1f163a5adacd9b67d8bb7f889e74fb8a8ff9acd3387eda5dad134f4bdfcb9b75486aeb9b6d9748f9d9c9bc83aa58889acfb7cba87faabf23d83bb008aed67af9cf7bbd47283aca0adee44f2b8a09ab872868cfe96c46f8189e5add33aac91fcb0c680a2b9b8a3d36af6af9eb7d037e2a3; WM_TID=QwhwuhoZTbBBABAREAJ8zo9oyYo9Wp6m; JSESSIONID-WYYY=feAGae5MO3glCkIpwT%2F%2FsJ%5CvV2%2Bkh4s0aC0HYbJ3AqXdKIdMj1vWZM0qKbzybPzZVXW%2FZsVMtpgUuJMqOBTPEJIGEBK7%2FIzifC4aCbOJtaQ2aleNgZxM8aN0%2Fe%5Cb5tMt97t6Uwyshaxun66xi3mqT9zuWh5Mba5HYe7%2Bf9Mo0VYiPIi%2B%3A1562141352776',
    'referer': 'http://music.163.com/',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
response = requests.get(url, headers=headers)
# 检测请求异常
response.raise_for_status()
response.encoding = response.apparent_encoding
html = response.text

soup = BeautifulSoup(html, 'lxml')
# 内联框架获取到json数据
json_info = soup.find("textarea", attrs={'id': 'song-list-pre-data'}).text
# 转为json对象
songs_info = json.loads(str(json_info))

book = xlwt.Workbook()
sheet1 = book.add_sheet('sheet1', cell_overwrite_ok=True)
sheet1.col(0).width = (10 * 256)
sheet1.col(1).width = (40 * 256)
sheet1.col(2).width = (30 * 256)
sheet1.col(3).width = (20 * 256)
sheet1.col(4).width = (30 * 256)
sheet1.col(5).width = (40 * 256)
sheet1.col(6).width = (30 * 256)
heads = ['排名', '歌曲名称', '专辑', '时长', '歌手', '链接', '发行时间']

# 写入表头
column = 0
for head in heads:
    sheet1.write(0, column, head)
    column += 1

# 写入歌曲信息
rank = 1
for song_info in songs_info:

    sheet1.write(rank, 0, rank)
    # 歌名
    name = song_info.get("name")
    sheet1.write(rank, 1, name)

    # 专辑
    album_name = song_info.get("album").get("name")
    sheet1.write(rank, 2, album_name)
    # 歌曲时长
    duration = song_info.get("duration") / 1000
    minute = str(int(duration / 60))
    second = str(int(duration % 60))
    if len(second) < 2:
        second = '0' + str(second)
    sheet1.write(rank, 3, minute+":"+second)

    # 歌手
    artists = song_info.get("artists")
    artists_name = artists[0].get("name")
    if len(artists) > 1:
        for index in range(1, len(artists)):
            artists_name += " / "+artists[index].get("name")
    sheet1.write(rank, 4, artists_name)

    # 链接
    song_id = song_info.get("id")
    href = "https://music.163.com/song?id="+str(song_id)
    sheet1.write(rank, 5, href)
    # 发行时间
    t1 = song_info.get("publishTime")
    publish_time = "not exist!"
    if t1 > 0:
        publish_time = time.strftime("%Y-%m-%d", time.localtime(t1 / 1000))
    sheet1.write(rank, 6, publish_time)
    rank += 1
    if rank > 51:
        break
    book.save('hot_top_50.xls')
