---
source_url: https://docs.dolphindb.cn/zh/funcs/h/hex.html
fetched_at: 2026-05-19T09:27:15Z
category: funcs
title: hex
sha1: ecc3eecb3365018290b7053377a55a993ca507a1
---

# hex

## 语法

`hex(X, [reverse=false])`

## 详情

把如下数据类型转换为十六进制数据显示：

- INTEGRAL
- FLOAT
- COMPLEX
- BINARY

注：

与 Python 的内置函数 `hex` 类似：

| 特性 | DolphinDB `hex` | Python `hex` |
| --- | --- | --- |
| 支持类型 | 整型、浮点、复数、二进制 | 仅整型 |
| 输入形式 | 标量、向量 | 仅标量 |
| 输出格式 | 完整字节表示（如 `"00000010"`） | 带 `0x` 前缀（如 `0x10`） |
| 字节序控制 | 支持 *reverse* 参数 | 无此功能 |

## 参数

**X** 是一个整型标量或向量。

**reverse** 是一个布尔值，表示高低位是否互换。默认值是 false。

## 返回值

STRING 类型的标量或向量，表示数据对应的十六进制数。

## 例子

```dolphindb
hex(16 25);
//output: ["00000010","00000019"]

hex(16 25,true);
//output: ["10000000","19000000"]

hex(compress(1 2 3));
//output: ["00","05","ff","01","04","04","00","00","ff","ff","ff","ff","03","00","00","00","ff","ff","ff","ff","0d","00","00","80","c0","01","00","00","00","02","00","00","00","03","00","00","00"]

a = hex(123.456 3.1415926)
print a
//output: ["405edd2f1a9fbe77","400921fb4d12d84a"]
```
