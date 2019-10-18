# 使用MySQL数据库

阅读: 27689     [评论](http://www.liujiangblog.com/course/django/165#comments)：6

在实际生产环境，Django是不可能使用SQLite这种轻量级的基于文件的数据库作为生产数据库。一般较多的会选择MySQL。

下面介绍一下如何在Django中使用MySQL数据库。

## 一、安装MySQL

![29.png-118.5kB](http://static.zybuluo.com/feixuelove1009/nbc2jwhltc1vxvloelf713i9/29.png)

不建议在Windows中部署MySQL，建议迁移到Linux上来。

我这里使用的是ubuntu16.04。

安装命令：

```
sudo apt-get update
sudo apt-get install mysql-server mysql-client
```

![30.png-42kB](http://static.zybuluo.com/feixuelove1009/g8wybha3kuqkax9rwf19aled/30.png)

中途，请设置root用户的密码。

安装完毕后，使用命令行工具，输入root的密码，进入mysql：

```
mysql -u root -p
```

提示如下：

```
[feixue@feixue-VirtualBox: ~]$ mysql -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 4
Server version: 5.7.20-0ubuntu0.16.04.1 (Ubuntu)

Copyright (c) 2000, 2017, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```

可以使用命令，先看看当前数据库系统内有哪些已经默认创建好了的数据库：

```
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.04 sec)
```

假设我们的Django工程名字为'mysite'，那么我们就创建一个mysite数据库，当然，名字其实随意，但是一样的更好记忆和区分，不是么？

```
CREATE DATABASE mysite CHARACTER SET utf8;
```

### 强调：一定要将字符编码设置为utf8，很多错误就是没正确设置编码导致的！

创建好mystie数据库后，可以用上面的命令，检查一下，没有问题，就退出mysql。

```
mysql> CREATE DATABASE mysite CHARACTER SET utf8;
Query OK, 1 row affected (0.00 sec)

mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysite             |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.00 sec)

mysql> exit;
Bye
```

## 二、配置MySQL服务

由于我的环境是局域网，Django项目所在主机为192.168.1.100，而mysql所在linux为虚拟机，IP为192.168.1.121，为了能够从项目主机访问数据库主机，需要对MySQL服务进行配置。

打开配置文件：

```
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
```

将下面一行注释掉：

```
# band-address = localhost
# .....

[mysqld]
#
# * Basic Settings
#
user            = mysql
pid-file        = /var/run/mysqld/mysqld.pid
socket          = /var/run/mysqld/mysqld.sock
port            = 3306
basedir         = /usr
datadir         = /var/lib/mysql
tmpdir          = /tmp
lc-messages-dir = /usr/share/mysql
skip-external-locking
#bind-address= localhost
skip-name-resolve
character-set-server=utf8

# .....
```

如果不这么做，将会出现`error：1045 deny access`，拒绝访问错误。

使用下面的命令，重新启动mysql服务：

```
sudo service mysql restart
```

## 三、安装Python访问MySQL的模块

我使用的是Python3.6版本。由于mysqldb-python这个模块不支持Python3.4以上版本，因此只能安装pymysql库。

```
pip install pymysql
```

## 四、配置Django的settings.py

在Django的settings.py文件中设置如下：

```
import pymysql         # 一定要添加这两行！           
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'mysite',  # 数据库名，先前创建的
        'USER': 'root',     # 用户名，可以自己创建用户
        'PASSWORD': '****',  # 密码
        'HOST': '192.168.1.121',  # mysql服务所在的主机ip
        'PORT': '3306',         # mysql服务端口
    }
}
```

重点是开始的两行！一定要添加，一定要这么写！

至此，就可以像使用SQLite一样使用MySQL了！