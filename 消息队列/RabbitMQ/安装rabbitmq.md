# [CentOS 7 下Erlang 20.2安装部署](https://ken.io/note/centos7-erlang-install)

## 一、前言

### 1、本篇文章适用范围

- Erlang 17.0+
- CentOS 7

### 2、本片环境信息

- CentOS 7.X
- Erlang 20.2

## 二、编译安装

### 1、安装准备

- 安装Erlang编译安装必要依赖

```bash
#安装必要依赖
sudo yum install -y gcc gcc-c++ glibc-devel make ncurses-devel openssl-devel autoconf java-1.8.0-openjdk-devel git
```

- 下载Erlang源码

下载地址：https://www.erlang.org/downloads

```bash
#进入下载目录
cd /home/download

#下载
wget http://erlang.org/download/otp_src_20.2.tar.gz
```

- 解压

```bash
tar -zvxf otp_src_20.2.tar.gz
```

### 2、Erlang安装

- 编译&安装

```bash
#进入根目录
cd otp_src_20.2.tar.gz

#编译&安装
./otp_build autoconf
./configure && make && sudo make install
```

- 验证

```bash
#进入erlang命令行表示成功
erl
```

## 三、YUM安装

### 1、安装准备

- 创建Yum源

```bash
#创建yum源
vim /etc/yum.repos.d/rabbitmq-erlang.repo

#文件内容
[rabbitmq-erlang]
name=rabbitmq-erlang
baseurl=https://dl.bintray.com/rabbitmq/rpm/erlang/20/el/7
gpgcheck=1
gpgkey=https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc
repo_gpgcheck=0
enabled=1
```

## 2、Erlang安装

- 安装

```bash
yum repolist
yum install -y erlang
```

- 验证

```bash
#进入erlang命令行表示成功
erl
```

## 四、备注

- 本文参考

https://github.com/erlang/otp/blob/maint/HOWTO/INSTALL.md

https://github.com/rabbitmq/erlang-rpm

https://zfanw.com/blog/install-erlang-on-centos-7.html



# [CentOS 7 下RabbitMQ 3.7 安装与配置](https://ken.io/note/centos7-rabbitmq-install-setup)

## 一、前言

### 1、本篇文章适用范围

- RabbitMQ 3.7+
- CentOS 7

### 2、本篇环境信息?

- CentOS 7.X
- Erlang 20.2（RabbitMQ要求是19.3-20.2.x）
- RabbitMQ 3.7.x

## 二、RabbitMQ安装

### 1、准备工作

- 安装Erlang(19.3+)

https://ken.io/note/centos7-erlang-install

- 安装 socat

```bash
sudo yum install -y socat
```

### 2、安装并启动

- RPM安装

官网下载地址：https://www.rabbitmq.com/install-rpm.html

```bash
sudo rpm -Uvh https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.3/rabbitmq-server-3.7.3-1.el7.noarch.rpm
```

> 如果遇到erlang已安装且版本正确，但是RabbitMQ检测失败的情况
> 可以追加参数 —nodeps （不验证软件包依赖）

- 启动RabbitMQ服务

```bash
#启动服务
sudo systemctl start rabbitmq-server

#查看状态
sudo systemctl status rabbitmq-server

#设置为开机启动
sudo systemctl enable rabbitmq-server
```

## 三、RabbitMQ配置

### 1、添加用户并授权

```bash
#添加用户
sudo rabbitmqctl add_user admin pwd

#设置用户角色
sudo rabbitmqctl set_user_tags admin administrator

#tag（administrator，monitoring，policymaker，management）

#设置用户权限(接受来自所有Host的所有操作)
sudo rabbitmqctl  set_permissions -p "/" admin '.*' '.*' '.*'  

#查看用户权限
sudo rabbitmqctl list_user_permissions admin
```

### 2、配置用户远程访问

```bash
#修改配置文件
sudo vi /etc/rabbitmq/rabbitmq.config 

#保存以下内容
[
{rabbit, [{tcp_listeners, [5672]}, {loopback_users, ["admin"]}]}
].
```

### 3、重启服务并开放端口

- 重启服务

```bash
sudo systemctl restart rabbitmq-server
```

- 开放端口

```bash
#开放端口
sudo firewall-cmd --add-port=5672/tcp --permanent

#重新加载防火墙配置
sudo firewall-cmd --reload
```

## 四、备注

### 1、RabbitMQ常用命令

```bash
# 添加用户
sudo rabbitmqctl add_user <username> <password>  

# 删除用户
sudo rabbitmqctl delete_user <username>  

# 修改用户密码
sudo rabbitmqctl change_password <username> <newpassword>  

# 清除用户密码（该用户将不能使用密码登陆，但是可以通过SASL登陆如果配置了SASL认证）
sudo rabbitmqctl clear_password <username> 

# 设置用户tags（相当于角色，包含administrator，monitoring，policymaker，management）
sudo rabbitmqctl set_user_tags <username> <tag>

# 列出所有用户
sudo rabbitmqctl list_users  

# 创建一个vhosts
sudo rabbitmqctl add_vhost <vhostpath>  

# 删除一个vhosts
sudo rabbitmqctl delete_vhost <vhostpath>  

# 列出vhosts
sudo rabbitmqctl list_vhosts [<vhostinfoitem> ...]  

# 针对一个vhosts给用户赋予相关权限；
sudo rabbitmqctl set_permissions [-p <vhostpath>] <user> <conf> <write> <read>  

# 清除一个用户对vhosts的权限；
sudo rabbitmqctl clear_permissions [-p <vhostpath>] <username>  

# 列出哪些用户可以访问该vhosts；
sudo rabbitmqctl list_permissions [-p <vhostpath>]   

# 列出用户访问权限；
sudo rabbitmqctl list_user_permissions <username>
```

### 2、本文参考

https://www.rabbitmq.com/download.html

https://github.com/judasn/Linux-Tutorial/blob/master/RabbitMQ-Install-And-Settings.md

http://blog.csdn.net/zyz511919766/article/details/42292655