---
source_url: https://docs.dolphindb.cn/zh/funcs/a/addVolumes.html
fetched_at: 2026-05-19T09:12:53Z
category: funcs
title: addVolumes
sha1: 0c27c1989612069033a78945e2dfebb760a92de9
---

# addVolumes

## 语法

`addVolumes(volumes)`

## 详情

动态增加磁盘卷，使新增磁盘卷马上可以使用而无需重启集群。

注：

此命令并不会改变集群配置文件。使用该命令后请更改配置文件，否则集群重启后将不能写入新增的磁盘卷。

## 参数

**volumes** 是字符串标量或向量，表示磁盘卷的路径。

## 例子

```dolphindb
addVolumes("/home/dolphindb/data")
```
