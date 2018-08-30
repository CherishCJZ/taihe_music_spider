# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

import pymysql

from taihe_music_spider.items import ThmsSingerItem, ThmsSongItem
from taihe_music_spider.settings import host, port, user, passwd, db


class TaiheMusicSpiderPipeline(object):

    def __init__(self):
        # 数据库连接参数
        self.conn = pymysql.connect( host=host,port=port,user=user, password=passwd,db = db)
        self.cur = self.conn.cursor()
        self.sql_insert_singer = 'INSERT INTO t_singer (singer_id, singer_name, singer_region, singer_birth, singer_face) VALUES (%s, %s, %s, %s, %s)'
        self.sql_insert_song = 'INSERT INTO t_song (song_id, song_name, song_link, song_lrc, singer_id, album_id) VALUES (%s, %s, %s, %s, %s, %s)'
        self.sql_insert_album = 'INSERT INTO t_album (album_id, album_name, album_link, release_date, company_name, singer_id) VALUES (%s, %s, %s, %s, %s, %s)'

        self.sql_get_saved_singer = "select singer_id from t_singer"
        self.sql_get_saved_song = "select song_id from t_song"
        self.sql_get_saved_album = "select album_id from t_album"


        self.saved_singer = self.init_saved_singer()
        self.saved_song = self.init_saved_song()
        self.saved_album = self.init_saved_album()

    def process_item(self, item, spider):
        if isinstance(item,ThmsSingerItem):
            self.saveSinger(item)
        elif isinstance(item,ThmsSongItem):
            self.saveSong(item)
        else:
            self.saveAlbum(item)
        return item

    def saveSinger(self,singer):
        if singer["singer_id"] not in self.saved_singer:
            try:
                self.cur.execute(self.sql_insert_singer, (singer["singer_id"], singer["singer_name"], singer["singer_region"], singer['singer_birth'], singer["singer_face"]))
                self.conn.commit()
            except BaseException as e:
                self.conn.rollback()
                print("保存singer出现异常，事务回滚。")
                print(e)
            finally:
                self.saved_singer.append(singer["singer_id"])



    def saveSong(self,song):
        if song["song_id"] not in self.saved_song:
            try:
                self.cur.execute(self.sql_insert_song, (song["song_id"], song["song_name"], song["song_link"], song["song_lrc"], song["singer_id"], song["album_id"]))
                self.conn.commit()
            except BaseException as e:
                self.conn.rollback()
                print("保存song出现异常，事务回滚。")
                print(e)
            finally:
                self.saved_song.append(song["song_id"])

    def saveAlbum(self,album):
        if album["album_id"] not in self.saved_album:
            try:
                self.cur.execute(self.sql_insert_album, (album["album_id"], album["album_name"], album["album_link"], album["release_date"], album["company_name"], album["singer_id"]))
                self.conn.commit()
            except BaseException as e:
                self.conn.rollback()
                print("保存album出现异常，事务回滚。")
                print(e)
            finally:
                self.saved_album.append(album["album_id"])
    def close_spider(self, spider):
        self.conn.close()


    def init_saved_singer(self):
        try:
            self.cur.execute(self.sql_get_saved_singer)
            return list(zip(*self.cur.fetchall()).__next__())
        except:
            return []

    def init_saved_song(self):
        try:
            self.cur.execute(self.sql_get_saved_song);
            return list(zip(*self.cur.fetchall()).__next__())
        except:
            return []

    def init_saved_album(self):
        try:
            self.cur.execute(self.sql_get_saved_album);
            return list(zip(*self.cur.fetchall()).__next__())
        except:
            return []

