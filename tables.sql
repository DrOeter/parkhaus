create database carpark;

use carpark;

create table user (
    user_id int NOT NULL AUTO_INCREMENT,
    plate varchar(20),
    seasonticket char(1),
    entrydate datetime,
    leavedate datetime,
    totaltime int,
    PRIMARY KEY (user_id)
);

create table space (
    space_id int NOT NULL,
    user_id int,
    occupied char(1),
    seasonticket char(1),
    PRIMARY KEY (space_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);