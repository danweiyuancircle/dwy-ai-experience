---
source_url: https://docs.dolphindb.cn/zh/funcs/s/saveAsNpy.html
fetched_at: 2026-05-19T09:37:49Z
category: funcs
title: saveAsNpy
sha1: 8708efe7796bb9b640e1818082d4a3187247daad
---

# saveAsNpy

## 语法

`saveAsNpy(obj, fileName)`

## 详情

将一个 DolphinDB 向量或矩阵保存为 Python Numpy 支持的 npy 格式的二进制文件。该函数必须要用户登录后才能执行。

注：*obj* 中的 NULL 值会转换为负无穷（-inf）。

## 参数

**obj** 是一个数值向量或矩阵。

**fileName** 是服务器端输出文件的绝对路径或相对路径。

## 例子

```dolphindb
v = 1..1000
v.saveAsNpy("/home/DolphinDB/intVec.npy")

m = (1..1000 + 0.5)$20:50
m.saveAsNpy("/home/DolphinDB/doubleMat.npy")
```

在 Python 中加载保存的文件。

```dolphindb
import numpy as np
v = np.load("/home/DolphinDB/intVec.npy")
m = np.load("/home/DolphinDB/doubleMat.npy")
```
