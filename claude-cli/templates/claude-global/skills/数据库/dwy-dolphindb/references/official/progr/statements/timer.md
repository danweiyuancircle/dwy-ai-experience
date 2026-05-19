---
source_url: https://docs.dolphindb.cn/zh/progr/statements/timer.html
fetched_at: 2026-05-19T09:02:04Z
category: progr
title: timer
sha1: 65d580e243ad389f1ad86ede6ff20ba1a0e84089
---

# timer

*timer* 语句用于计算一条命令的执行时间。

## 语法

| 用法 | 语法 |
| --- | --- |
| 1 | ```dolphindb timer{ <statement block> } ``` |
| 2 | ```dolphindb timer (X){ <statement block> } ``` |

## 参数

对于第二种用法，**X** 是正整数，表示连续（非并行）执行指定代码块的次数。

## 详情

计算执行指定代码的耗费的时间。

注：

timer
获取的耗时仅为脚本在服务器运行的时间（若为集群环境，包含集群内节点间的网络开销），不包括客户端和服务器之间的网络传输耗时。

## 例子

```dolphindb
x=rand(10.0, 1000000);

timer x*2;
// output
Time elapsed: 3 ms

timer(10){x*2};
// output
Time elapsed: 35.004 ms
```
