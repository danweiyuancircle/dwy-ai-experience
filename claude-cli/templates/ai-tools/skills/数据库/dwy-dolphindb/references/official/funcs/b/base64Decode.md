---
source_url: https://docs.dolphindb.cn/zh/funcs/b/base64Decode.html
fetched_at: 2026-05-19T09:13:37Z
category: funcs
title: base64Decode
sha1: 19325f154c71653c95489f356c28e88d9859518b
---

# base64Decode

## 语法

`base64Decode(X)`

## 详情

将 Base64 编码的数据解码为二进制数据。

## 参数

**X** 字符串标量或向量。

## 返回值

BLOB 类型标量或向量。

## 例子

```dolphindb
base64Decode(base64Encode(`hello))
// output
hello

base64Decode(base64Encode(`hello`world))
// output
["hello","world"]
```

相关函数：[base64Encode](base64Encode.html)
