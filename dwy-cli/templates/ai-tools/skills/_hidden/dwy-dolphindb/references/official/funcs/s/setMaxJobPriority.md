---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setMaxJobPriority.html
fetched_at: 2026-05-19T09:38:44Z
category: funcs
title: setMaxJobPriority
sha1: 60aee0f40231b1060645481077e6a81a8a21ab71
---

# setMaxJobPriority

## 语法

`setMaxJobPriority(userId, maxPriority)`

## 详情

为给定用户指定其提交作业的最高优先级。该函数必须要用户登录后才能执行。

注：

该函数可在控制节点、数据节点和计算节点运行。

## 参数

**userId** 是一个字符串，表示用户名。

**maxPriority** 是一个0到8之间的整数，表示给定用户提交作业的最高优先级。

## 例子

```dolphindb
login(`admin,`123456)
createUser(`KyleMurray, `Cardinals2020QB)
setMaxJobPriority(`KyleMurray, 7);
```
