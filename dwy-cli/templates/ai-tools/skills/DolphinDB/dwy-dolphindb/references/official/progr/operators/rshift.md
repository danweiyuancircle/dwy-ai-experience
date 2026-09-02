---
source_url: https://docs.dolphindb.cn/zh/progr/operators/rshift.html
fetched_at: 2026-05-19T09:01:30Z
category: progr
title: rshift(>>)
sha1: 1dd19cd0a8640080742872d58db22825096ecbe1
---

# rshift(>>)

## 语法

`X>>a`

## 参数

- **X** 可以是整数标量、数据对、向量或矩阵；
- **a** 是要移的位数。

## 详情

*rshift* 是将X按二进制展开后整体往右移动a位数。原来右侧的位数被截去。

## 例子

```dolphindb
rshift(2048, 2);
// output
512

1..10 >> 1;
// output
[0,1,1,2,2,3,3,4,4,5]

1:10>>1;
// output
0 : 5
```

相关函数： [lshift](lshift.html)
