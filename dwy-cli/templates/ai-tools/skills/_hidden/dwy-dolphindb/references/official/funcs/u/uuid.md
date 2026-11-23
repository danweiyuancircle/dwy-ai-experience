---
source_url: https://docs.dolphindb.cn/zh/funcs/u/uuid.html
fetched_at: 2026-05-19T09:43:32Z
category: funcs
title: uuid
sha1: be369827d12fe2d606f1a2f4119e1f8efba8913b
---

# uuid

## 语法

`uuid(X)`

## 详情

把字符串转换成 UUID 类型。通过 rand(uuid(), n) 可以随机生成 n 个 UUID 类型的数据。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

UUID 类型标量或向量。

## 例子

```dolphindb
uuid("");
```

返回：00000000-0000-0000-0000-000000000000

```dolphindb
a=uuid("9d457e79-1bed-d6c2-3612-b0d31c1881f6");
a;
```

返回：9d457e79-1bed-d6c2-3612-b0d31c1881f6

```dolphindb
typestr(a);
```

返回：UUID
