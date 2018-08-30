create table t_singer(
	singer_id varchar(15) primary key,
	singer_name varchar(50),
	singer_region varchar(50),
	singer_birth date,
	singer_face varchar(255)
)engine=innodb default charset=utf8


create table t_album(
	album_id varchar(15) primary key,
	album_name varchar(50),
	album_link varchar(255),
	release_date date,
	company_name varchar(50),
	singer_id varchar(50),
	constraint fk_t_album_singer_singerid foreign key(singer_id) references t_singer(singer_id),
)engine=innodb default charset=utf8


create table t_song(
	song_id varchar(15) primary key,
	song_name varchar(50),
	song_link varchar(255),
	song_lrc text,
	singer_id varchar(15),
	album_id varchar(15),
	constraint fk_t_song_singer_singerid foreign key(singer_id) references t_singer(singer_id),
	constraint fk_t_song_album_albumid foreign key(album_id) references t_album(album_id)
)engine=innodb default charset=utf8


# 外键会导致存储出现异常



