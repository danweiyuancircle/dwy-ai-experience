---
source_url: https://docs.dolphindb.cn/zh/funcs/b/base64Encode.html
fetched_at: 2026-05-19T09:13:39Z
category: funcs
title: base64Encode
sha1: 896a857f31a0fa236c7a0438c1db176b40676615
---

# base64Encode

## 语法

`base64Encode(X)`

## 详情

将 *X* 转换为 Base64 编码格式。

## 参数

**X** 字符串标量或向量。

## 返回值

字符串标量或向量。

## 例子

```dolphindb
base64Encode(`hello) 
// output
aGVsbG8=

base64Encode(`hello`world) 
// output
["aGVsbG8=","d29ybGQ="]

base64Encode("")
// output
""
```

相关函数：[base64Decode](base64Decode.html)
