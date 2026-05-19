---
source_url: https://docs.dolphindb.cn/zh/progr/statements/Include.html
fetched_at: 2026-05-19T09:01:57Z
category: progr
title: Include
sha1: 3bb5836ca79a81664878c3ddd47721ca1931265c
---

# Include

## 语法

`#include "file path"`

## 参数

**file path** 字符串，表示服务器端文件的绝对路径或相对路径。

## 详情

语句#include可以导入用户脚本。#include不能在命令行中使用。

## 例子

在下例中，脚本"GetTable.txt"使用#include语句导入"/home/test/"目录下名为"GenTradeTable.txt"的脚本文件。

GenTradeTable.txt的内容：

```dolphindb
n=2000
syms=`YHOO`GE`MS`MSFT`JPM`ORCL`CISCO
timestamp=09:30:00+rand(18000, n)
sym=rand(syms, n)
qty=100*(1+rand(100,n))
price=5.0+rand(100.0, n)
t1=table(timestamp,sym,qty,price);
```

GetTable.txt的内容：

```dolphindb
#include "/home/test/GenTradeTable.txt"
t1;
```

执行以下语句：

```dolphindb
run "GetTable.txt";
```

| timestamp | sym | qty | price |
| --- | --- | --- | --- |
| 12:19:25 | YHOO | 9500 | 93.307309 |
| 11:02:57 | GE | 8400 | 52.797873 |
| 10:04:09 | CISO | 1700 | 57.467623 |
| 12:01:23 | JPM | 8300 | 70.12557 |
| 14:22:02 | MS | 7900 | 44.220769 |
| ... |
