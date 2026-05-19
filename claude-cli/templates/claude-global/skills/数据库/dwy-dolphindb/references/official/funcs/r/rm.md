---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rm.html
fetched_at: 2026-05-19T09:36:34Z
category: funcs
title: rm
sha1: a611d8a9595be0188066e6ab456897a84ece5062
---

# rm

## 语法

`rm(filename)`

## 详情

删除一个文件。该命令必须要用户登录后才能执行。

## 参数

**filename** 是要删除的文件的名称。

## 例子

```dolphindb
files("/home/test");
```

| filename | isDir | fileSize | lastAccessed | lastModified |
| --- | --- | --- | --- | --- |
| abc.txt | 0 | 15 | 2017.06.05 08:09:47.443 | 2017.06.05 07:24:19.999 |
| dir1 | 1 | 0 | 2017.06.05 08:06:44.836 | 2017.06.05 08:06:44.836 |
| dir2 | 1 | 0 | 2017.06.05 08:06:42.210 | 2017.06.05 08:06:42.210 |
| dir3 | 1 | 0 | 2017.06.05 08:06:39.597 | 2017.06.05 08:06:39.597 |

```dolphindb
rm("/home/test/abc.txt");       // delete file abc.txt

files("/home/test");
```

| filename | isDir | fileSize | lastAccessed | lastModified |
| --- | --- | --- | --- | --- |
| dir1 | 1 | 0 | 2017.06.05 08:06:44.836 | 2017.06.05 08:06:44.836 |
| dir2 | 1 | 0 | 2017.06.05 08:06:42.210 | 2017.06.05 08:06:42.210 |
| dir3 | 1 | 0 | 2017.06.05 08:06:39.597 | 2017.06.05 08:06:39.597 |
