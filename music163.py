# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import xlwt
import time
import datetime
import threading
import logging


class music163(object):

    @staticmethod
    def write_book_header(book_sheet, book_headers):
        column = 0
        for head in book_headers:
            book_sheet.write(0, column, head)
            column += 1

    @staticmethod
    def get_songs_info(request_url, request_header):
        response = requests.get(request_url, headers=request_header)
        # 检测请求异常
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # 内联框架获取到json数据
        json_info = soup.find("textarea", attrs={'id': 'song-list-pre-data'}).text
        # 转为json对象
        songs_info = json.loads(str(json_info))
        logging.info("获取热歌榜json数据，总条数：{%ld}", len(songs_info))
        return songs_info

    # 生成热歌榜Excel
    @staticmethod
    def write_hot_music(songs_info, write_sheet, write_book):
        # 写入歌曲信息
        rank = 1
        songs_arr = []
        for song_info in songs_info:

            write_sheet.write(rank, 0, rank)
            # 歌名
            name = song_info.get("name")
            write_sheet.write(rank, 1, name)

            # 专辑
            album_name = song_info.get("album").get("name")
            write_sheet.write(rank, 2, album_name)
            # 歌曲时长
            duration = song_info.get("duration") / 1000
            minute = str(int(duration / 60))
            second = str(int(duration % 60))
            if len(second) < 2:
                second = '0' + str(second)
            write_sheet.write(rank, 3, minute + ":" + second)

            # 歌手
            artists = song_info.get("artists")
            artists_name = artists[0].get("name")
            if len(artists) > 1:
                for index in range(1, len(artists)):
                    artists_name += " & " + artists[index].get("name")
            write_sheet.write(rank, 4, artists_name)

            # 链接
            song_id = song_info.get("id")
            href = "https://music.163.com/song?id=" + str(song_id)
            write_sheet.write(rank, 5, href)

            # 发行时间
            t1 = song_info.get("publishTime")
            publish_time = "not exist!"
            if t1 > 0:
                publish_time = time.strftime("%Y-%m-%d", time.localtime(t1 / 1000))
            write_sheet.write(rank, 6, publish_time)
            rank += 1
            songs_arr.append({
                "name": name,
                "singer": artists_name,
                "song_id": song_id
            })
            if rank > 51:
                break
        write_book.save(datetime.datetime.now().strftime('%Y-%m-%d')+"_网易云音乐热歌榜TOP50.xls")
        return songs_arr

    # 生成热评Excel
    @staticmethod
    def record_hot_comments(song_id, song_name, singer):
        comments_url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(song_id) + '?csrf_token='
        comments_hearder = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'referer': 'https://music.163.com/song?id=' + str(song_id)
        }
        data = {
            'params': 'FlmfdDay0U2q8ZBEDwVhmQ378fPm/SbVQJlwdXyIQ0UtypDWC4UXvOcg7w/cZOmROgBFpCkuw4+HpKue8euK34xsXyBgfK1n0W8vMf82XXxjjPR7nf/z9lQoWPTJG+nMRmBDj2CcEq7/nLIExmPv5dgB2m4MieG8wJIzaKfGV4ZtqrzE4ensTk3NdrkcJuo0',
            'encSecKey': '334cda06516d25aa0ad5b6f74241c9a49ebc0e1370d60aeb54028ae963631a75969a5f922cef267407747d7de18be94900219207bd39145b5ea01ec6349168e1ca73bca54b33a4de71b69e4c0ce0717a4c561bc93592a5e59d67fc4192dd204c19901a142677b624c69fe2b0297423cfef87df955eb071326b00edf3c8be5634'
        }

        # 获取json格式的评论
        comments = requests.post(comments_url, data=data, headers=comments_hearder)
        comments.raise_for_status()
        comments.encoding = "utf-8"

        hot_comments = json.loads(str(comments.text)).get("hotComments")
        hot_comments_book = xlwt.Workbook()
        hot_comments_sheet = hot_comments_book.add_sheet('sheet1', cell_overwrite_ok=True)
        hot_comments_sheet.col(0).width = (30 * 256)
        hot_comments_sheet.col(1).width = (150 * 256)
        hot_comments_sheet.col(2).width = (15 * 256)
        hot_comments_header = ['昵称', '评论内容', '点赞数']

        music163.write_book_header(hot_comments_sheet, hot_comments_header)
        count = 1
        for hot_comment in hot_comments:
            nick_name = hot_comment.get("user").get("nickname")
            content = hot_comment.get("content")
            liked_count = hot_comment.get("likedCount")
            hot_comments_sheet.write(count, 0, nick_name)
            hot_comments_sheet.write(count, 1, content)
            hot_comments_sheet.write(count, 2, liked_count)
            count += 1
        if song_name == "Señorita":
            logging.error("爬取热歌榜的热评：名称：{%s}, 热评总数：{%s}", str(song_name).encode(encoding="utf-8"), count)
        else:
            logging.info("爬取热歌榜的热评：名称：{%s}, 热评总数：{%s}", song_name, count)

        hot_comments_book.save(datetime.datetime.now().strftime('%Y-%m-%d')+"_"+song_name+"_"+singer+"_热评.xls")


if __name__ == '__main__':

    # 实例化handler
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='music163.log',
                        filemode='w')
    start_time = time.time()
    logging.info('-----------------开始爬取网易云热歌榜---')
    # 热歌榜内联链接
    url = "https://music.163.com/discover/toplist?id=3778678"

    # 添加请求头
    headers = {
        'cookie': '_iuqxldmzr_=32; _ntes_nnid=a662d3c2e4f2914fd042904bd19585b0,1562137812793; _ntes_nuid=a662d3c2e4f2914fd042904bd19585b0; WM_NI=fxRIla05f8Trg1PxAyCSnPrigsd87wIi8hdEtx1yN9E3k9R80c4X4XFrwUZxMCTzE2gXGKxpzY6Js7Ae0inmmD9ZQzAtPLoH2hPy5zFT2uAeCW%2BLP2hO4OGtbgxBPb6qRVM%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeacb37b9af5e195e66d88a88ab6c85e878f8faeb866adb0c09ae73fb89cbdd8b22af0fea7c3b92aa6a89eaaef6bf4ebaad9d77aa5efa099c473818da2b1f163a5adacd9b67d8bb7f889e74fb8a8ff9acd3387eda5dad134f4bdfcb9b75486aeb9b6d9748f9d9c9bc83aa58889acfb7cba87faabf23d83bb008aed67af9cf7bbd47283aca0adee44f2b8a09ab872868cfe96c46f8189e5add33aac91fcb0c680a2b9b8a3d36af6af9eb7d037e2a3; WM_TID=QwhwuhoZTbBBABAREAJ8zo9oyYo9Wp6m; JSESSIONID-WYYY=feAGae5MO3glCkIpwT%2F%2FsJ%5CvV2%2Bkh4s0aC0HYbJ3AqXdKIdMj1vWZM0qKbzybPzZVXW%2FZsVMtpgUuJMqOBTPEJIGEBK7%2FIzifC4aCbOJtaQ2aleNgZxM8aN0%2Fe%5Cb5tMt97t6Uwyshaxun66xi3mqT9zuWh5Mba5HYe7%2Bf9Mo0VYiPIi%2B%3A1562141352776',
        'referer': 'http://music.163.com/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

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
    music163.write_book_header(sheet1, heads)

    # 获取热歌榜信息
    songs = music163.get_songs_info(url, headers)
    # 写入热歌榜数据
    song_arr = music163.write_hot_music(songs, sheet1, book)
    for song in song_arr:
        # 多线程获取热评数据
        t = threading.Thread(target=music163.record_hot_comments,
                             args=(song.get("song_id"), song.get("name"), song.get("singer")))
        # 启动线程
        t.start()
    t.join()
    end_time = time.time()
    logging.info("--------------------网易云热歌榜爬取完成,总用时：{%f}", (end_time-start_time))

