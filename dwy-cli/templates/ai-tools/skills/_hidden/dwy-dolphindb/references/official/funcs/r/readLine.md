---
source_url: https://docs.dolphindb.cn/zh/funcs/r/readLine.html
fetched_at: 2026-05-19T09:35:18Z
category: funcs
title: readLine
sha1: 693a1308c8d58f37ee10c9af3976604065eeb09b
---

# readLine

## 语法

`readLine(handle)`

## 详情

从给定的文件中读取一行。

## 参数

**handle** 是文件句柄。

## 返回值

返回的行不包括换行符。如果文件结束，函数会返回一个 NULL 对象，可以用 [isVoid](../i/isVoid.html)
函数测试。

## 例子

```dolphindb
x=`IBM`MSFT`GOOG`YHOO`ORCL;
eachRight(writeLine, file("test.txt","w"), x);

// output
[1,1,1,1,1]

fin = file("test.txt")
do{
x=fin.readLine()
if(x.isVoid()) break
print x
}while(true);

// output
IBM
MSFT
GOOG
YHOO
ORCL
```
