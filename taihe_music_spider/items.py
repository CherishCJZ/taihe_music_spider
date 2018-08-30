# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


from scrapy.item import Item, Field


class ThmsSingerItem(Item):

    # 歌手
    singer_id = Field()
    singer_name = Field()
    singer_region = Field()
    singer_birth = Field()
    singer_face = Field()

class ThmsSongItem(Item):
    song_id = Field()
    # 歌名
    song_name = Field()
    # 歌曲在百度mp3中的url
    song_link = Field()
    # 歌词
    song_lrc = Field()
    singer_id = Field()
    album_id = Field()

class ThmsAlbumItem(Item):

    album_id = Field()
    # 所属专辑
    album_name = Field()
    album_link = Field()
    # 专辑发行时间
    release_date = Field()
    # 所属公司
    company_name = Field()

    singer_id = Field()


