---
source_url: https://docs.dolphindb.cn/zh/funcs/c/close.html
fetched_at: 2026-05-19T09:15:23Z
category: funcs
title: close
sha1: 7ac42cd0b836b03d60cfceb7b78012be81c889e6
---

# close

## 语法

`close(X)`

## 详情

关闭一个已打开的文件或远程连接。该函数必须要用户登录后才能执行。

## 参数

**X** 是一个文件句柄或远程连接。

## 返回值

无。

## 例子

```dolphindb
fout=file("test.txt","w");
fout.writeLine("hello world!");
// output
1
fout.close();
fin = file("test3.txt");
print fin.readLine();
hello world!
fin.close();
```
