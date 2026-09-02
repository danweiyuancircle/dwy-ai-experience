---
source_url: https://docs.dolphindb.cn/zh/progr/rfc.html
fetched_at: 2026-05-19T09:02:40Z
category: progr
title: 远程函数调用
sha1: 5245d5d259a43b3642521c62050f91d759009f35
---

# 远程函数调用

有两种方式可以执行远程调用：

- 远程调用一个内置函数
- 远程运行一个用户定义的本地函数

## 语法

建立一个远程连接：

```dolphindb
host = xdb(URL, Port)
```

远程调用：

```dolphindb
host("functionName", functionParameters)
```

或

```dolphindb
remoteRun(host, "functionName", functionParameters)
remoteRunWithCompression(host, "functionName", functionParameters) // 压缩传输
```

## 远程系统函数调用

```dolphindb
h=xdb("localhost",80);
h("sum",rand(100, 1000));
// output
50971

remoteRun(h, "sum", rand(100, 1000));
// output
48704

remoteRunWithCompression(h, "sum", rand(100, 1000))
// output
49964
```

## 远程用户定义函数调用

```dolphindb
def f1(a): sin(rand(100.0,a))
def f2(a,b):return b+f1(a)
pools=each(xdb, "localhost",82)
result = peach(remoteRun{, f2, 100, 0.5}, pools) // result = peach(remoteRunWithCompression{, f2, 100, 0.5}, pools)
result;
```
