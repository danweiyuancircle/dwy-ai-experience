---
source_url: https://docs.dolphindb.cn/zh/tutorials/nginx_dolphindb.html
fetched_at: 2026-05-19T09:49:50Z
category: tutorials
title: 通过 Nginx 反向代理 DolphinDB 集群节点
sha1: 8d27354a1f6385214eabd61916401a57df0bb399
---

# 通过 Nginx 反向代理 DolphinDB 集群节点

## 1. 概述

本教程详细介绍如何通过 Nginx 实现 DolphinDB 服务器集群的反向代理，支持 WebSocket（适用于浏览器和 VSCode 客户端）和 TCP（适用于
Python API 等客户端）协议，并提供 SSL 加密连接支持。

### 1.1 Nginx 介绍

Nginx 是一款高性能的开源 Web 服务器，同时也可用作反向代理服务器、负载均衡器和 HTTP 缓存。凭借其高并发处理能力和低资源消耗特性，Nginx
常用于为后端服务提供统一的访问入口。通过 Nginx 的反向代理和负载均衡功能，我们可以将客户端请求分发到多个 DolphinDB
集群节点上，从而提高系统的可用性和响应速度。在 DolphinDB 高可用架构中，引入 Nginx 作为前端入口，具有以下优势：

- **安全与灵活性：** 通过 Nginx，可以方便地对外隐藏 DolphinDB
  后端节点的真实信息，并可在代理层增加访问控制、日志记录以及未来扩展 HTTPS 等功能。
- **统一入口与负载均衡：** Nginx 可监听一个统一的服务地址（如域名），将进入的请求根据配置的策略转发给后端的 DolphinDB
  集群各节点。通过 `upstream` 配置，我们将多个 DolphinDB
  服务节点组成上游组，实现简单的**轮询负载均衡**，避免单点压力过大，提高集群吞吐能力。
- **故障切换：** 当某个后端节点发生故障时，Nginx 能自动将请求转发至其他健康节点（取决于
  `proxy_next_upstream` 等设置），从而在一定程度上实现故障转移，增强 DolphinDB
  服务的高可用性。

需要注意的是，由于增加了一层代理，客户端请求需经由 Nginx 再到
DolphinDB，这会引入一次额外的网络转发，在高负载情况下可能带来轻微的性能下降。本教程将详细介绍在 DolphinDB 高可用集群场景下部署 Nginx
并实现反向代理的方法。

整体架构如图，Nginx 反向代理，可以通过客户端（浏览器、VS Code、API）访问后端多个 DolphinDB 集群节点。

![](images/nginx_dolphindb/1-1.png)

图 1. Websocket 协议下反向代理架构

### 1.2 环境说明

在开始部署之前，先说明本次示例的环境和参数设定：

- **操作系统：** CentOS 7.9 (64位) 或同等的 Linux 发行版，已安装基本的编译工具和库（如 GCC、Make
  等）。
- **DolphinDB 集群：** 已部署完成一个包含 **3 台服务器节点** 的 DolphinDB 集群。假设各节点 IP
  和角色如下：
  - 节点1：`192.168.1.10:8902` – 数据节点
  - 节点2：`192.168.1.11:8902` – 数据节点
  - 节点3：`192.168.1.12:8902` – 控制节点
- **Nginx 部署节点：**`192.168.1.20` – 将在此节点安装
  Nginx，用作集群的反向代理入口（也可选择集群内部某台机器部署 Nginx）。Nginx 将监听80和81端口，对外提供服务，并将请求转发至
  DolphinDB 后端端口 `8902`。
- **软件版本：** DolphinDB 集群版本为 **3.00.2.3** 。Nginx 使用官方稳定版
  **1.22.0**（源码编译安装），编译依赖 PCRE 库版本 **8.45**（用于支持正则和Rewrite功能）。

上述环境中，各服务器之间网络互通，防火墙已放行必要端口（比如 80 和 8902）。读者在实际操作时，请根据自己环境的 IP 和端口进行调整。

## 2. 配置步骤

### 2.1 安装并启动 Nginx

下面详细记录在 Linux 上源码编译安装 Nginx 并进行基础配置的过程，包括 PCRE 库的准备、编译选项以及启动验证步骤。

#### 2.1.1 安装依赖工具

首先，确保系统已安装编译所需的基本工具和库开发包。在 CentOS 下可以使用 yum 安装，在 Debian/Ubuntu 下使用 apt
安装。例如，在 CentOS 执行：

```dolphindb
yum -y install gcc zlib zlib-devel pcre-devel openssl openssl-devel
```

上述命令安装了GNU 编译器，以及 zlib、OpenSSL、PCRE 等库的开发头文件。特别地，**PCRE（Perl Compatible
Regular Expression）** 是 Nginx 用于处理正则匹配（如 rewrite 和 location）的必要依赖。安装
`pcre` 和 `pcre-devel` 可以提供 PCRE
支持；若不安装，在编译 Nginx 时会报错找不到 PCRE。在本教程中我们也展示如何通过源码编译方式集成 PCRE。

#### 2.1.2 下载 Nginx 和 PCRE 源码

从官方源获取 Nginx 和 PCRE 压缩包：

```dolphindb
mkdir -p /usr/local/webserver && cd /usr/local/webserver
```

```dolphindb
wget https://nginx.org/download/nginx-1.22.0.tar.gz && wget http://downloads.sourceforge.net/project/pcre/pcre/8.45/pcre-8.45.tar.gz
```

解压安装包：

```dolphindb
tar -zxvf nginx-1.22.0.tar.gz && tar -zxvf pcre-8.45.tar.gz
```

上述下载了 Nginx 1.22.0 和 PCRE 8.45 的源码压缩包并解压。通过源码编译 PCRE，我们可以在编译 Nginx
时静态链接该库，从而**无需依赖系统已安装的 PCRE**。

#### 2.1.3 编译安装 Nginx（包含 PCRE）

进入解压后的 Nginx 源码目录，配置编译选项并编译。

编译 PCRE ：

```dolphindb
cd /usr/local/webserver/pcre-8.45 && ./configure
```

```dolphindb
make && make install
```

查看`pcre-8.45` 的版本：

```dolphindb
pcre-config --version
```

编译 Nginx：

```dolphindb
cd /usr/local/webserver/nginx-1.22.0 && ./configure --prefix=/usr/local/webserver/nginx --with-http_stub_status_module --with-http_ssl_module --with-pcre=/usr/local/webserver/pcre-8.45 --with-stream --with-stream_ssl_module
```

```dolphindb
make && make install
```

在 `./configure` 中，`--with-pcre=../pcre-8.45`
指定了 PCRE 源码路径，配置系统会自动编译该 PCRE 并将其静态链接到 Nginx 二进制中。另外我们启用了
`stub_status_module`（可选，用于状态监控）、
`http_ssl_module`（如将来需要支持 HTTPS）`stream`
和`stream_ssl_module`（如需要TCP连接和SSL加密）。`--prefix=/usr/local/nginx`
指定了安装目录。`make install` 完成后，Nginx 文件将安装到该目录下：

- 主配置文件：`/usr/local/webserver/nginx/conf/nginx.conf`
- 可执行文件：`/usr/local/webserver/nginx/sbin/nginx`
- 日志目录：`/usr/local/webserver/nginx/logs/`

#### 2.1.4 启动 Nginx 并验证

执行以下命令启动 Nginx：

```dolphindb
/usr/local/webserver/nginx/sbin/nginx
```

默认情况下 Nginx 将以守护进程方式启动。如果需要停止或重启，可以使用
`/usr/local/webserver/nginx/sbin/nginx -s stop`
(快速停止) 或 `-s reload` (热加载配置)。首次启动前，建议使用
`-t` 检查配置文件语法：

```dolphindb
/usr/local/webserver/nginx/sbin/nginx -t
```

若输出显示 `syntax is ok` 和 `test is
successful`，表示配置文件没有语法错误。此时在浏览器中访问 Nginx 部署节点的 IP（例如
http://192.168.1.20/），如果看到默认的欢迎页面则表示 Nginx 安装启动成功。

### 2.2 WebSocket 协议下通过 Nginx 反向代理 DolphinDB

该方法适用于通过浏览器或 VS Code 端访问 DolphinDB。

#### 2.2.1 打开 nginx.conf 配置文件

通常位于:

```dolphindb
/usr/local/webserver/nginx/conf/nginx.conf
```

#### 2.2.2 编辑文件，修改全局、events和 HTTP 部分配置

可以直接复制下面配置内容：

```dolphindb
worker_processes auto;  # 工作进程数量，auto 表示自动检测CPU核心数
error_log /usr/local/webserver/nginx/logs/error.log;
pid /usr/local/webserver/nginx/logs/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;  # 每个工作进程最大并发连接数
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /usr/local/webserver/nginx/logs/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";

    proxy_connect_timeout 5s;
    proxy_read_timeout 60s;
    proxy_send_timeout 60s;
    proxy_buffers 16 32k;
    proxy_buffer_size 64k;
    proxy_busy_buffers_size 128k;

    include /etc/nginx/conf.d/*.conf;

}
```

此配置是全局配置和 HTTP 连接性能优化部分，包括：

- `proxy_http_version` 设置 HTTP/1.1，以支持 WebSocket
  协议升级和长连接。
- `proxy_set_header` 是为了保留客户端 IP 和 Host 头信息，以便 DolphinDB
  后端做记录/鉴权/日志分析。
- `proxy_read_timeout` 在 `http {}`
  块中设置的是全局默认值，表示超过该时间无消息传入则断开连接。如果在某个 `server {}` 或
  `location {}`
  块中**重新指定了该参数**，那么该局部设置会**覆盖全局配置**。对于 WebSocket
  连接，建议设置更长的超时时间，以避免因静止时间过长而中断。

#### 2.2.3 添加连接节点配置

这些配置需要根据实际 DolphinDB 节点 IP 和代理端口填写，添加到上述的 `http {}` 块中：

```dolphindb
# 定义上游服务器集群
upstream dolphindb_data {
    least_conn;
    server 192.168.1.10:8902;
    server 192.168.1.11:8902;
}

upstream dolphindb_control {
    server 192.168.1.12:8902;
}
    
server {
    listen 80;                # 监听端口80
    server_name  _;                 # 匹配任意主机名（下划线表示默认主机）
    location / {
        proxy_pass http://dolphindb_data;   # 转发请求到上游数据节点
        proxy_http_version 1.1;                # 使用HTTP/1.1与后端通信
        proxy_set_header Host $host;           # 保留原始Host头
        proxy_set_header X-Real-IP $remote_addr;        # 传递客户端真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # 记录代理链IP
        # WebSocket 配置：
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # 超时配置：
        proxy_connect_timeout 30s;
        proxy_read_timeout 7d;
        proxy_send_timeout 7d;
    }
}

server {
    listen 81;                # 监听端口81
    server_name  _;                 # 匹配任意主机名（下划线表示默认主机）
    location / {
        proxy_pass http://dolphindb_control;   # 转发请求到上游控制节点
        proxy_http_version 1.1;                # 使用HTTP/1.1与后端通信
        proxy_set_header Host $host;           # 保留原始Host头
        proxy_set_header X-Real-IP $remote_addr;        # 传递客户端真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # 记录代理链IP
        # WebSocket 配置：
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        # 超时配置：
        proxy_connect_timeout 30s;
        proxy_read_timeout 7d;
        proxy_send_timeout 7d;
    }
}
```

**配置说明：**

- `upstream`定义了一个上游服务器集群，名称为
  `dolphindb_cluster`。里面列出了三台后端 DolphinDB
  节点的地址和端口。默认情况下，不指定策略即为轮询（round-robin）方式，每个请求依次轮流分配到不同节点上。设定`least_conn`表示选择较少连接的服务器（least\_conn）优先。
- `server` 定义了前端代理服务的监听行为。`listen 80;` 指定在
  80 端口接受客户端请求。`server_name _;` 使用下划线 \_
  作为服务名，表示一个通配的默认主机（意味着无论请求的 Host
  为何，都由此虚拟主机处理）。在实际部署中，如果有特定域名，可在此处指定。
- `location /`
  来匹配所有以`/`开头的请求路径（即对整个站点的请求都处理）。
  - `proxy_pass`
    指定了请求转发的目标：`http://dolphindb_cluster`。这里使用了上面定义的上游集群名称。
  - `proxy_set_header`
    和相关指令用于配置当前`server`块代理转发时的HTTP请求头和连接参数，与上一步中的http全局配置含义相同。为了提高代理的健壮性，我们设置了一些超时参数：
  - `proxy_connect_timeout 30s;` 定义连接后端 DolphinDB
    的超时时间（握手超时）。如果在10秒内无法建立与任一后端的TCP连接，Nginx 将返回错误。
  - `proxy_send_timeout 7d;` 定义向后端发送请求数据的超时时间。
  - `proxy_read_timeout 7d;`
    定义从后端读取响应的**静默超时时间**。默认值为60秒，如果超过60秒后端没有任何响应数据发送，Nginx
    将关闭该连接。对于 WebSocket 长连接场景，建议将此值适当延长，否则当连接空闲超过60秒时，Nginx
    会认为后端不响应而切断连接，导致 WebSocket 意外断开（浏览器会收到 1006
    异常码）。本例将其延长至7d。总之，`proxy_read_timeout`
    要根据业务情况（如数据推送频率）进行调整，以平衡及时释放闲置连接和保持长连接不断开的需求。

#### 2.2.4 重载 Nginx 激活上述配置

当我们完成这些配置并保存到 `nginx.conf` 后，可以重载 Nginx：

```dolphindb
/usr/local/webserver/nginx/sbin/nginx -s reload
```

此时，Nginx 会在 80 端口等待请求，并按照配置将请求反向代理到 DolphinDB 集群的各节点上。

#### 2.2.5 访问方式

在浏览器中输入:

```dolphindb
http://nginx地址IP:配置中的监听端口
```

或在 VSCode DolphinDB 插件中Connection的配置中添加:

```dolphindb
"dolphindb.connections": [
    {
        "name": "nginx",
        "url": "ws://nginx地址IP:配置中的监听端口",
        "autologin": true,
        "username": "admin",
        "password": "123456"
    }
]
```

### 2.3 TCP 协议下通过 Nginx 反向代理 DolphinDB

该方法适用于Python API或其他API中连接DolphinDB。

![](images/nginx_dolphindb/2-1.png)

图 2. TCP 协议下反向代理架构

#### 2.3.1 编辑 nginx.conf 文件

与 `http {}` 同级下方，添加 stream {} 块，用82和83端口反向代理数据和控制节点：

```dolphindb
stream {
    upstream dolphindb_data {
        server 192.168.1.10:8902;
        server 192.168.1.11:8902;
    }
    server {
        listen 82;
        proxy_pass dolphindb_data;
    }

    upstream dolphindb_control {
        server 192.168.1.12:8902;
    }
    server {
        listen 83;
        proxy_pass dolphindb_control;
    }
}
```

注：

**stream块和http块中配置的端口（80，81）不能一样，**否则会因为 Nginx
不能自动识别TCP/HTTP协议转发而报错。

#### 2.3.2 重载 Nginx

```dolphindb
/usr/local/webserver/nginx/sbin/nginx -s reload
```

#### 2.3.3 在 Python 中连接

```dolphindb
import dolphindb as ddb
s = ddb.session()
s.connect("192.168.1.20", 82)  # 或 83
```

### 2.4 使用 SSL 加密 WebSocket 和 TCP 代理

在实际部署过程中，若需对Nginx 反向代理 DolphinDB 的 HTTP 接口（浏览器，客户端，VScode）与 TCP通信接口（如用于
Jupyter、Python api等）进行SSL/TLS加密，此处以上文中的控制节点为例，有以下步骤：

#### 2.4.1 确保 Nginx 下载时已启用此配置

```dolphindb
--with-http_ssl_module --with-stream_ssl_module
```

#### 2.4.2 修改 Nginx 配置文件的 http 部分

```dolphindb
http{
    upstream dolphindb_control {
        server 192.168.1.12:8902;
    }
    
    server {
        listen 81 ssl; 
        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers         AES128-SHA:AES256-SHA:RC4-SHA:DES-CBC3-SHA:RC4-MD5;
        ssl_certificate     /path/to/server.crt;
        ssl_certificate_key /path/to/server.key;
        
        location / {
            proxy_pass http://dolphindb_control;
            proxy_http_version  1.1;
            
            proxy_set_header    Host            $host;
            proxy_set_header    X-Real-IP       $remote_addr;
            proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
            
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            
            proxy_connect_timeout 30s;
            proxy_read_timeout 7d;
            proxy_send_timeout 7d;
        }
    }
}
```

和无SSL加密时的主要配置区别：

- `listen 81` 后增加了 `ssl`
- 指定了 SSL 协议和加密方法
- 指定了必要的 SSL
  证书与头信息的地址，可以无需CA，使用openssl以下指令自颁发生成自签名证书和私钥:

  ```dolphindb
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
  ```

#### 2.4.3 修改 Nginx 配置文件的 stream 部分

```dolphindb
stream {
    upstream dolphindb_control {
        server 192.168.1.12:8902;
    }
    
    server {
        listen 83 ssl; 
        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers         AES128-SHA:AES256-SHA:RC4-SHA:DES-CBC3-SHA:RC4-MD5;
        ssl_certificate     /path/to/server.crt;
        ssl_certificate_key /path/to/server.key;
        proxy_pass dolphindb_control;
    }
}
```

#### 2.4.4 重载 Nginx

```dolphindb
/usr/local/webserver/nginx/sbin/nginx -s reload
```

#### 2.4.5 访问方法

端口 81：用于 Web HTTPS访问控制节点，`https://192.168.1.20:81/`。

端口 83：用于 API 访问控制节点，TCP over SSL 的代理转发，此时的ddb连接配置需加一项
`enableSSL=True`。

```dolphindb
import dolphindb as ddb
s = ddb.session(enableSSL=True)
s.connect("192.168.1.20", 83)
```

## 3. 常见问题解答（FAQ）

### 3.1 WebSocket 握手失败（错误码 1006）

如果在通过 Nginx 访问 DolphinDB 的 WebSocket 服务时，前端报错 `code: 1006, reason:
"abnormal closure"` 或 `Connection header must include
'Upgrade`*'*，通常是由于握手协议头未正确转发导致的。解决办法是确保在 Nginx 配置中包含
`proxy_http_version 1.1;` 以及 `Upgrade` 和
`Connection` 头设置。

`proxy_set_header Upgrade $http_upgrade;` 将客户端请求中的 “Upgrade”
头的值传递给后端（一般为 “websocket”），而 `proxy_set_header Connection
"upgrade";` 则明确告诉后端希望升级连接。这两个指令是实现 WebSocket 握手的关键，缺少它们会导致后端无法识别为
WebSocket 请求，从而握手失败。例如，后端可能报出 *“Connection header must include 'Upgrade'”*
之类的错误。配置了以上头信息后，Nginx 收到 WebSocket 请求会将协议升级所需的头信息正确地传递给 DolphinDB 后端，使 WebSocket
可以建立长连接。

此处简单地将 Connection 固定设为 "upgrade" 来配合 Upgrade 头。如果还需要同时兼顾普通 HTTP 请求长连接，可以使用 Nginx
内置变量更优雅地处理。例如利用 `map` 指令，根据 `$http_upgrade` 是否为空设置
`$connection_upgrade` 变量为 "upgrade" 或 "close"，然后
`proxy_set_header Connection $connection_upgrade;`。这样既满足
WebSocket 升级，也不会在非 WebSocket请求时误设 Connection。但对 DolphinDB API 的场景而言，大部分请求可能涉及
WebSocket（如 Web 前端交互或流数据订阅），所以本文直接使用固定值简化配置。

### 3.2 多节点下启用了 keepalive 导致连接失败

在单节点情况下，`upstream` 配置中启用 `keepalive`
时，可以提升性能（避免每次重建TCP连接），但在多节点情况下，对于 WebSocket 这类**长寿命连接**而言，可能出现某些副作用。Nginx
无法感知连接是否还被 WebSocket 占用，容易误用被挂起的连接。因此在多节点状况下，请确保无类似 `keepalive
16;` 的配置。

### 3.3 每次登录到的节点不一样

在默认轮询策略或者本文配置的负载均衡策略（`least_conn`）下，每个请求可能落到不同的后端节点。如果应用场景对“会话粘性”有要求（例如某一用户登录后的所有请求应由同一节点处理），可在
`upstream` 配置中将 `least_conn` 改为
`ip_hash;`，这会根据客户端 IP 将请求固定转发到同一个后端节点。

### 3.4 VS Code 访问成功，浏览器访问不成功

清除浏览器缓存重试。

## 4. 附录

WebSocket 和TCP 示例完整配置文件：[nginx.conf](script/nginx_dolphindb/nginx.zip)。

SSL加密的WebSocket 和TCP 示例完整配置文件：[nginx\_ssl.conf](script/nginx_dolphindb/nginx_ssl.zip)。
