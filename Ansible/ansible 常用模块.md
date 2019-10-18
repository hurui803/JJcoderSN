# ansible 常用模块

------

常用的模块。根据官方的分类，将模块按功能分类为：云模块、命令模块、数据库模块、文件模块、资产模块、消息模块、监控模块、网络模块、通知模块、包管理模块、源码控制模块、系统模块、单元模块、web设施模块、windows模块 ，具体可以参看官方页面。这里从官方分类的模块里选择最常用的一些模块进行介绍（commands模块上一篇已经介绍，这里不再提）。

#### 一、ping模块

测试主机是否是通的，用法很简单，不涉及参数：

```shell
ansible 10.212.52.252 -m ping10.212.52.252 | success >> {"changed": false,"ping": "pong"}
```

#### 二、setup模块

setup模块，主要用于获取主机信息，在playbooks里经常会用到的一个参数gather_facts就与该模块相关。setup模块下经常使用的一个参数是filter参数，具体使用示例如下（由于输出结果较多，这里只列命令不写结果）：

```shell
ansible 10.212.52.252 -m setup -a 'filter=ansible_*_mb' //查看主机内存信息ansible 10.212.52.252 -m setup -a 'filter=ansible_eth[0-2]' //查看地接口为eth0-2的网卡信息
ansible all -m setup --tree /tmp/facts //将所有主机的信息输入到/tmp/facts目录下，每台主机的信息输入到主机名文件中（/etc/ansible/hosts里的主机名）
```

#### 三、file模块

file模块主要用于远程主机上的文件操作，file模块包含如下选项：

force：需要在两种情况下强制创建软链接，一种是源文件不存在但之后会建立的情况下；另一种是目标软链接已存在,需要先取消之前的软链，然后创建新的软链，有两个选项：yes|no

- group：定义文件/目录的属组
- mode：定义文件/目录的权限
- owner：定义文件/目录的属主
- path：必选项，定义文件/目录的路径
- recurse：递归的设置文件的属性，只对目录有效
- src：要被链接的源文件的路径，只应用于state=link的情况
- dest：被链接到的路径，只应用于state=link的情况
- state：  
    - directory：如果目录不存在，创建目录
    - file：即使文件不存在，也不会被创建
    - link：创建软链接
    - hard：创建硬链接
    - touch：如果文件不存在，则会创建一个新的文件，如果文件或目录已存在，则更新其最后修改时间
    - absent：删除目录、文件或者取消链接文件

使用示例：

```shell
ansible test -m file -a "src=/etc/fstab dest=/tmp/fstab state=link"
ansible test -m file -a "path=/tmp/fstab state=absent"
ansible test -m file -a "path=/tmp/test state=touch"
```

#### 四、copy模块

复制文件到远程主机，copy模块包含如下选项：

- backup：在覆盖之前将原文件备份，备份文件包含时间信息。有两个选项：yes|no
- content：用于替代"src",可以直接设定指定文件的值
- dest：必选项。要将源文件复制到的远程主机的绝对路径，如果源文件是一个目录，那么该路径也必须是个目录
- directory_mode：递归的设定目录的权限，默认为系统默认权限
- force：如果目标主机包含该文件，但内容不同，如果设置为yes，则强制覆盖，如果为no，则只有当目标主机的目标位置不存在该文件时，才复制。默认为yes
- others：所有的file模块里的选项都可以在这里使用
- src：要复制到远程主机的文件在本地的地址，可以是绝对路径，也可以是相对路径。如果路径是一个目录，它将递归复制。在这种情况下，如果路径使用"/"来结尾，则只复制目录里的内容，如果没有使用"/"来结尾，则包含目录在内的整个内容全部复制，类似于rsync。
- validate ：The validation command to run before copying into place. The path to the file to validate is passed in via '%s' which must be present as in the visudo example below.

示例如下：

```shell
ansible test -m copy -a "src=/srv/myfiles/foo.conf dest=/etc/foo.conf owner=foo group=foo mode=0644"
ansible test -m copy -a "src=/mine/ntp.conf dest=/etc/ntp.conf owner=root group=root mode=644 backup=yes"
ansible test -m copy -a "src=/mine/sudoers dest=/etc/sudoers validate='visudo -cf %s'"
```

#### 五、service模块

**用于管理服务**该模块包含如下选项：

- arguments：给命令行提供一些选项
- enabled：是否开机启动 yes|no
- name：必选项，服务名称
- pattern：定义一个模式，如果通过status指令来查看服务的状态时，没有响应，就会通过ps指令在进程中根据该模式进行查找，如果匹配到，则认为该服务依然在运行
- runlevel：运行级别
- sleep：如果执行了restarted，在则stop和start之间沉睡几秒钟
- state：对当前服务执行启动，停止、重启、重新加载等操作（started,stopped,restarted,reloaded）

使用示例：

```shell
# Example action to reload service httpd, in all cases
- service: name=httpd state=reloaded
# Example action to enable service httpd, and not touch the running state
- service: name=httpd enabled=yes
# Example action to start service foo, based on running process /usr/bin/foo
- service: name=foo pattern=/usr/bin/foo state=started
# Example action to restart network service for interface eth0
- service: name=network state=restarted args=eth0
```

#### 六、cron模块

**用于管理计划任务**包含如下选项：

- backup：对远程主机上的原任务计划内容修改之前做备份
- cron_file：如果指定该选项，则用该文件替换远程主机上的cron.d目录下的用户的任务计划
- day：日（1-31，*，*/2,……）
- hour：小时（0-23，*，*/2，……）
- minute：分钟（0-59，*，*/2，……）
- month：月（1-12，*，*/2，……）
- weekday：周（0-7，*，……）
- job：要执行的任务，依赖于state=present
- name：该任务的描述
- special_time：指定什么时候执行，参数： reboot,yearly,annually,monthly,weekly,daily,hourly
- state：确认该任务计划是创建还是删除
- user：以哪个用户的身份执行

示例：

```shell
ansible test -m cron -a 'name="a job for reboot" special_time=reboot job="/some/job.sh"'
ansible test -m cron -a 'name="yum autoupdate" weekday="2" minute=0 hour=12 user="rootansible 10.212.52.252 -m cron -a 'backup="True" name="test" minute="0" hour="2" job="ls -alh > /dev/null"'ansilbe test -m cron -a 'cron_file=ansible_yum-autoupdate state=absent'
```

#### 七、yum模块

使用yum包管理器来管理软件包，其选项有：

- config_file：yum的配置文件
- disable_gpg_check：关闭gpg_check
- disablerepo：不启用某个源
- enablerepo：启用某个源
- name：要进行操作的软件包的名字，也可以传递一个url或者一个本地的rpm包的路径
- state：状态（present，absent，latest）

示例如下：

```shell
ansible test -m yum -a 'name=httpd state=latest'
ansible test -m yum -a 'name="@Development tools" state=present'
ansible test -m yum -a 'name=http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm state=present'
```

#### 八、user模块与group模块

user模块是请求的是useradd, userdel, usermod三个指令，goup模块请求的是groupadd, groupdel, groupmod 三个指令，具体参数这里不再细讲，直接上示例。

1、user模块示例：

```shell
- user: name=johnd comment="John Doe" uid=1040 group=admin- user: name=james shell=/bin/bash groups=admins,developers append=yes
- user: name=johnd state=absent remove=yes- user: name=james18 shell=/bin/zsh groups=developers expires=1422403387#生成密钥时，只会生成公钥文件和私钥文件，和直接使用ssh-keygen指令效果相同，不会生成authorized_keys文件。- user: name=test generate_ssh_key=yes ssh_key_bits=2048 ssh_key_file=.ssh/id_rsa
```

**注：**指定password参数时，不能使用后面这一串密码会被直接传送到被管理主机的/etc/shadow文件中，所以需要先将密码字符串进行加密处理。然后将得到的字符串放到password中即可。

```shell
openssl passwd -1 -salt $(< /dev/urandom tr -dc '[:alnum:]' | head -c 32)Password:$1$YngB4z8s$atSVltYKnDxJmWZ3s.4/80或者
echo "123456" | openssl passwd -1 -salt $(< /dev/urandom tr -dc '[:alnum:]' | head -c 32) -stdin$1$4P4PlFuE$ur9ObJiT5iHNrb9QnjaIB0#经验证下面生成的密码串也可以正常使用，不过与/etc/shadow的格式不统一，不建议使用
openssl passwd -salt -1 "123456"-1yEWqqJQLC66#使用上面的密码创建用户
ansible all -m user -a 'name=foo password="$1$4P4PlFuE$ur9ObJiT5iHNrb9QnjaIB0"'
```

不同的发行版默认使用的加密方式可能会有区别，具体可以查看/etc/login.defs文件确认，centos 6.5版本使用的是SHA512加密算法，生成密码可以通过ansible官方给出的示例：

```
python -c "from passlib.hash import sha512_crypt;import getpass; print sha512_crypt.encrypt(getpass.getpass())"
```

2、group示例

```
- group: name=somegroup state=present
```

#### 九、synchronize模块

使用rsync同步文件，其参数如下：

- archive: 归档，相当于同时开启recursive(递归)、links、perms、times、owner、group、-D选项都为yes ，默认该项为开启
- checksum: 跳过检测sum值，默认关闭
- compress:是否开启压缩
- copy_links：复制链接文件，默认为no ，注意后面还有一个links参数
- delete: 删除不存在的文件，默认no
- dest：目录路径
- dest_port：默认目录主机上的端口 ，默认是22，走的ssh协议
- dirs：传速目录不进行递归，默认为no，即进行目录递归
- rsync_opts：rsync参数部分
- set_remote_user：主要用于/etc/ansible/hosts中定义或默认使用的用户-与rsync使用的用户不同的情况
- mode: push或pull 模块，push模的话，一般用于从本机向远程主机上传文件，
- pull 模式用于从远程主机上取文件

另外还有其他参数，这里不再一一说明。上几个用法：

```
src=some/relative/path dest=/some/absolute/path rsync_path="sudo rsync"src=some/relative/path dest=/some/absolute/path archive=no links=yessrc=some/relative/path dest=/some/absolute/path checksum=yes times=nosrc=/tmp/helloworld dest=/var/www/helloword rsync_opts=--no-motd,--exclude=.git mode=pull
```

#### 十、mount模块

**配置挂载点**选项：

- dump
- fstype：必选项，挂载文件的类型
- name：必选项，挂载点
- opts：传递给mount命令的参数
- src：必选项，要挂载的文件
- state：必选项present：只处理fstab中的配置
- absent：删除挂载点
- mounted：自动创建挂载点并挂载之'
- umounted：卸载

示例：

```
name=/mnt/dvd src=/dev/sr0 fstype=iso9660 opts=ro state=presentname=/srv/disk src='LABEL=SOME_LABEL' state=presentname=/home src='UUID=b3e48f45-f933-4c8e-a700-22a159ec9077' opts=noatime state=presentansible test -a 'dd if=/dev/zero of=/disk.img bs=4k count=1024'ansible test -a 'losetup /dev/loop0 /disk.img'ansible test -m filesystem 'fstype=ext4 force=yes opts=-F dev=/dev/loop0'ansible test -m mount 'name=/mnt src=/dev/loop0 fstype=ext4 state=mounted opts=rw'
```

#### 十一、get_url 模块

该模块主要用于从http、ftp、https服务器上下载文件（类似于wget），主要有如下选项：

- sha256sum：下载完成后进行sha256 check；
- timeout：下载超时时间，默认10s
- url：下载的URL
- url_password、url_username：主要用于需要用户名密码进行验证的情况
- use_proxy：是事使用代理，代理需事先在环境变更中定义

示例：

```
- name: download foo.confget_url: url=http://example.com/path/file.conf dest=/etc/foo.conf mode=0440- name: download file with sha256 checkget_url: url=http://example.com/path/file.conf dest=/etc/foo.conf sha256sum=b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b878ae4944c
```

模块部分就先介绍到这里吧，官方提供的可能用到模块有git、svn版本控制模块，sysctl 、authorized_key_module系统模块，apt、zypper、pip、gem包管理模块，find、template文件模块，mysql_db、redis数据库模块，url 网络模块等。具体可以参看官方手册模块部分;