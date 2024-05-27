---
pinned: true
title: 北邮python大作业-共享单车管理系统
created: '2024-05-13T10:34:23.727Z'
modified: '2024-05-27T08:50:56.078Z'
---

## 北邮python大作业-共享单车管理系统
### 功能介绍
为了实现简单，与课程实验要求更贴近，故改写共享单车管理系统。
1. 权限管理
权限分为客户和staff，客户只能租赁和归还共享单车，staff可以删除和增加共享单车。
2. 租赁与归还
使用bool量存放租赁状态，当被占用时拒绝新的租赁请求。
3. 删除与增加
以id作为主键。
4. 后续可添加功能
租金计算、损坏报修、再做一个数据库来放订单

### 数据结构&对象关系
用户只有类user，其中身份字段代表权限。
单车类中包括id、租赁状态。

### 技术栈
#### 前端：(react)
#### 后端：python、flask框架
#### 数据库：pymysql

#### 5月20号补充:
1. 链接数据库定义游标过于重复，后期可封装减少冗余

### mysql建表语句
请首先创建数据库bike，并选为默认数据库，以下是建表语句：
### user：
CREATE TABLE `user` (
  `userid` int NOT NULL AUTO_INCREMENT,
  `position` enum('staff','customer') NOT NULL,
  `isrenting` tinyint NOT NULL DEFAULT '0',
  `username` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`username`),
  UNIQUE KEY `userid_UNIQUE` (`userid`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

### bike：
CREATE TABLE `bike` (
  `bikeid` int NOT NULL AUTO_INCREMENT,
  `rentable` tinyint NOT NULL DEFAULT '1',
  `userid` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`bikeid`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


