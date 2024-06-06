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

#### 5月30号日志:
队友做出了订单记录和计算费用系统<br>
目前基础flask程序已经构建完毕，包括功能注册登录、租赁归还、增加删除，能够在flask网页上正常工作。
##### 后续计划：
数据可视化：matplotlib，结合订单数据库显示订单时间段（设想）
减少数据库操作函数库部分（test.py）的代码冗余（我来弄）

#### 5月31号凌晨:
通过建立一个数据库链接管理类，不必在每个函数中创建新的链接，大大降低了代码冗余度。

#### 6月3号:
增加了三个url /img /select /predict
增加了供数据可视化和预测的取数操作
增加了数据可视化和预测的程序
增加了requirements
在对数据库的操作上增加了锁
增加了两个网页 select供选择可视化指标 img供显示图片

### mysql建表语句
请首先创建数据库bike，并选为默认数据库，以下是建表语句：（新增orders表）
### user：
CREATE TABLE `user` (<br>
  `userid` int NOT NULL AUTO_INCREMENT,<br>
  `position` enum('staff','customer') NOT NULL,<br>
  `isrenting` tinyint NOT NULL DEFAULT '0',<br>
  `username` varchar(45) NOT NULL,<br>
  `password` varchar(45) NOT NULL,<br>
  PRIMARY KEY (`username`),<br>
  UNIQUE KEY `userid_UNIQUE` (`userid`),<br>
  UNIQUE KEY `username_UNIQUE` (`username`)<br>
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;<br>

### bike：
CREATE TABLE `bike` (<br>
  `bikeid` int NOT NULL AUTO_INCREMENT,<br>
  `rentable` tinyint NOT NULL DEFAULT '1',<br>
  `userid` varchar(45) DEFAULT NULL,<br>
  PRIMARY KEY (`bikeid`)<br>
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;<br>

### orders
CREATE TABLE `orders` (<br>
  `orderid` int NOT NULL AUTO_INCREMENT,<br>
  `userid` int DEFAULT NULL,<br>
  `bikeid` int DEFAULT NULL,<br>
  `start_time` datetime DEFAULT NULL,<br>
  `end_time` datetime DEFAULT NULL,<br>
  `total_time` float DEFAULT NULL,<br>
  `total_cost` float DEFAULT NULL,<br>
  PRIMARY KEY (`orderid`)<br>
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;<br>