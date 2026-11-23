---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mkdir.html
fetched_at: 2026-05-19T09:31:59Z
category: funcs
title: mkdir
sha1: 64fe937451d50cdce27cae6433b987697e73baf8
---

# mkdir

## 语法

`mkdir(directory)`

## 详情

创建一个目录。该函数必须要用户登录后才能执行。

## 参数

**directory** 为要创建的目录的名字。

## 返回值

无。

## 例子

```dolphindb
files("/home/test");
```

| filename | isDir | fileSize | lastAccessed | lastModified |
| --- | --- | --- | --- | --- |
| dir3 | 1 | 0 | 2017.06.05 08:06:39.597 | 2017.06.05 08:06:39.597 |

```dolphindb
mkdir("/home/test/dir1");
mkdir("/home/test/dir2");
mkdir("/home/test/dir3");
// output
The directory [/home/test/dir3] already exists.
```

```dolphindb
files("/home/test");
```

| filename | isDir | fileSize | lastAccessed | lastModified |
| --- | --- | --- | --- | --- |
| dir1 | 1 | 0 | 2017.06.05 08:33:48.372 | 2017.06.05 08:33:48.372 |
| dir2 | 1 | 0 | 2017.06.05 08:34:05.598 | 2017.06.05 08:34:05.598 |
| dir3 | 1 | 0 | 2017.06.05 08:06:39.597 | 2017.06.05 08:06:39.597 |
