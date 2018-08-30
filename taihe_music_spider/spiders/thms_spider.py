# -*- coding: utf-8 -*-
import scrapy,re
import json
from bs4 import BeautifulSoup
from taihe_music_spider.items import ThmsSingerItem,ThmsSongItem,ThmsAlbumItem
from urllib import parse
from random import Random
import logging


class TaiheMusicSpider(scrapy.Spider):


    name = 'thms'
    allowed_domains = ['music.taihe.com']
    start_urls = ['http://music.taihe.com/artist']
    song_num = 0
    # 自定义属性
    host = 'http://music.taihe.com'
    page_size = 15
    url_template = "http://music.taihe.com/data/user/getsongs?start={}&size={}&ting_uid={}&.r={}"
    lrc_url_template = "http://music.taihe.com/data/song/lrc?lrc_link={}"
    r = Random()
    birth_pattern = re.compile("\d{4}-\d{2}-\d{2}")



    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('TaiheMusicSpider')
        logger.setLevel(logging.DEBUG)
        super().__init__(*args, **kwargs)

    def parse(self, response):
        '''从入口地址[歌手列表开始抓取]'''
        # print(type(response))
        # 进入单页抓取
        for link in self.get_singer_links(response):
            yield scrapy.Request(link,callback=self.parse_singer)


    def parse_singer(self, response):
        '''歌手单页抓取歌手信息以及歌曲列表'''

        singer_item = ThmsSingerItem()
        singer_id = response.url.strip('/').rsplit('/', 1)[1]
        singer_item["singer_name"],singer_item['singer_face'],singer_item["singer_region"],singer_item["singer_birth"] = self.get_singer_datails(response)
        singer_item["singer_id"] = singer_id
        yield singer_item

        # print(item)
        page_num = self.get_page_num(response)

        for page in range(page_num):
            start = page * self.page_size
            url = str.format(self.url_template,start,self.page_size,singer_id,self.r.random())
            yield scrapy.Request(url,method="post",meta={"singer_id":singer_id},callback=self.parse_songs)



    def parse_songs(self, response):
        for song_link in self.get_song_links(response):
            yield scrapy.Request(song_link,meta={"singer_id":response.meta["singer_id"]},callback=self.parse_song)


    def parse_song(self,response):
        soup = BeautifulSoup(response.text,"lxml")
        song_info_tag = soup.find("div",class_="song-info-box fl")
        song_lrc_tag = soup.find("div",id="lyricCont")
        song_link = response.url
        singer_id = response.meta["singer_id"]
        song_id = response.url.strip('/').rsplit('/', 1)[1]
        song_name = self.get_song_name(song_info_tag)
        album_name,album_link,release_date,company_name = self.get_album_info(song_info_tag)
        album_id = album_link.strip('/').rsplit('/', 1)[1]

        album_item = ThmsAlbumItem()
        album_item["album_id"] = album_id
        album_item["album_name"] = album_name
        album_item["album_link"] = album_link
        album_item["release_date"] = release_date
        album_item["company_name"] = company_name
        album_item["singer_id"] = singer_id
        yield album_item

        song_item = ThmsSongItem()
        song_item["song_id"] = song_id
        song_item["song_name"] = song_name
        song_item["song_link"] = song_link
        song_item["singer_id"] = singer_id
        song_item["album_id"] = album_id

    #     self.fill_song_lrc(song_lrc_tag,item,response.url)
    #
    #
    # def fill_song_lrc(self, song_lrc_tag,item,referer):
        song_lrc_link = song_lrc_tag.attrs["data-lrclink"].strip() if song_lrc_tag else None
        if song_lrc_link:
            headers = {"Referer":response.url}
            song_lrc_link = str.format(self.lrc_url_template,song_lrc_link)
            yield scrapy.Request(song_lrc_link,headers=headers,callback=self.parse_song_lrc,meta={"song_item":song_item})

    def parse_song_lrc(self,response):
        song_item = response.meta["song_item"]
        response_map = json.loads(response.text,encoding="utf-8")
        song_lrc = response_map.get("content")
        song_lrc = re.sub("\[.*?\]","",song_lrc).strip()
        song_item["song_lrc"] = song_lrc
        return song_item

    def get_song_name(self,song_info_tag):
        song_name_tag = song_info_tag.find("span",class_="name")
        if song_name_tag:
            return song_name_tag.get_text()

    def get_album_info(self,song_info_tag):
        album__desc_tag = song_info_tag.find("p",class_="album desc")
        album_release_date_tag = song_info_tag.find("p",class_="publish desc")
        album_company_tag = song_info_tag.find("p",class_="company desc")
        album_name = ""
        album_link = ""
        release_date = "1970-01-01"
        company_name = ""
        if album__desc_tag:
            album_name = album__desc_tag.a.get_text()
            album_link = parse.urljoin(self.host,album__desc_tag.a.get("href"))

        if album_release_date_tag:
            release_date = album_release_date_tag.get_text()
            if "："  in release_date:
                release_date = release_date.split("：")[1]

        if album_company_tag:
            company_name = album_company_tag.get_text()
            if "："  in company_name:
                company_name = company_name.split("：")[1]

        return album_name,album_link,release_date,company_name


    def get_page_num(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        page_tags = soup.find("div",class_="page-cont").find_all("a",class_="page-navigator-number PNNW-S")
        assert isinstance(page_tags,list)
        max_page = 1
        if page_tags:
            max_page = page_tags[-1].get_text().strip()
        return int(max_page)





    def get_song_links(self,response):
        content_map = json.loads(response.text, encoding="utf-8")
        html = content_map.get("data").get("html")
        soup = BeautifulSoup(str(html), "lxml")
        song_links = []
        for song_tag in soup.find_all("a",href=re.compile("/song/\d+")):
            song_links.append(parse.urljoin(self.host,song_tag.attrs["href"]))
        return song_links


    def get_singer_links(self,response):
        soup = BeautifulSoup(response.text,"lxml")
        singer_links = []
        artist_tags = soup.find_all("a", href=re.compile("/artist/\d+"))
        for artist_tag in artist_tags:
            link = artist_tag.attrs["href"]
            if link not in singer_links:
                singer_links.append(parse.urljoin(self.host,link.strip()))
        return singer_links

    def get_singer_datails(self,response):
        soup = BeautifulSoup(response.text, "lxml")
        name_tag = soup.find("span",class_="artist-name")
        face_tag =  soup.find("img",class_="music-artist-img")
        area_tag = soup.find("span",class_="area")
        birth_tag = soup.find("span",class_="birth")
        singer_name = ""
        singer_face = ""
        singer_region = ""
        singer_birth = "1970-01-01"
        if name_tag:
            singer_name = re.sub("\s+"," ",name_tag.get_text().strip())
        if face_tag:
            singer_face = face_tag.attrs["src"]
            singer_face = parse.urljoin(self.host,singer_face)
        if area_tag:
            singer_region = re.sub("\s+"," ",area_tag.get_text().strip())
            singer_region = singer_region.split("： ")[1] if "： " in singer_region else singer_region
        if birth_tag:
            singer_birth = re.sub("\s+"," ",birth_tag.get_text().strip())
            singer_birth = singer_birth.split("： ")[1] if "： " in singer_birth else singer_birth
            singer_birth = self.birth_pattern.match(singer_birth).group()
        return singer_name,singer_face,singer_region,singer_birth







