---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sleep.html
fetched_at: 2026-05-19T09:39:28Z
category: funcs
title: sleep
sha1: 88de5dc68af5f6a261c521f16d5c929f215e227c
---

# sleep

## 语法

`sleep(X)`

## 详情

暂停程序 *X* 毫秒。

## 参数

**X** 是一个非负数。

## 例子

```dolphindb
for(s in 1:10){
   sleep(1000)
   print(s+" seconds passed.")
};

// output
1 seconds passed.
2 seconds passed.
3 seconds passed.
4 seconds passed.
5 seconds passed.
6 seconds passed.
7 seconds passed.
8 seconds passed.
9 seconds passed.
```
