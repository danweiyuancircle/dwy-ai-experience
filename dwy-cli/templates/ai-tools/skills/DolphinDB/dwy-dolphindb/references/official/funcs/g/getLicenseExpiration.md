---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getLicenseExpiration.html
fetched_at: 2026-05-19T09:24:51Z
category: funcs
title: getLicenseExpiration
sha1: 19ba8e09fdd1643ee24c05b955403b03aa5076b1
---

# getLicenseExpiration

## 语法

`getLicenseExpiration()`

## 详情

查看当前节点的 license 过期时间。可用于更新 license 之后，验证新的 license 是否生效。

## 参数

无

## 返回值

DATE 类型标量。

## 例子

```dolphindb
getLicenseExpiration()
```

输出返回：2021.09.30
