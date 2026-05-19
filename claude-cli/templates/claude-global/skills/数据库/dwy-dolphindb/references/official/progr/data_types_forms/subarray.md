---
source_url: https://docs.dolphindb.cn/zh/progr/data_types_forms/subarray.html
fetched_at: 2026-05-19T09:00:33Z
category: progr
title: 子数组（subarray）
sha1: e377941bf0498bb32575c4af21f298b9b9d60f99
---

# 子数组（subarray）

当使用某个向量的一部分元素进行计算时，例如若使用 `close[10:].avg()` 的语句，系统会从向量
close 中复制数据产生一个新的向量close[10:]再进行计算，不仅占用更多内存而且耗时。

`subarray`
函数返回输入向量的一个子向量。它是原向量的一个视图，只记录了原向量的指针以及子向量的开始和结束位置。由于并没有分配大块内存来存储新向量，所以没有发生数据复制。所有向量的只读操作都可直接应用于
`subarray`。

`subarray` 函数的语法如下：

`subarray(X, range)`

例1：

```dolphindb
x=1..100
subarray(x, 10:20);

[11,12,13,14,15,16,17,18,19,20]

subarray(x, 90:);

[91,92,93,94,95,96,97,98,99,100]

subarray(x, :10);

[1,2,3,4,5,6,7,8,9,10]
```

例2：

```dolphindb
a=rand(1000.0,20000000);
timer a.subarray(0:1000000).avg();

Time elapsed: 1.5 ms
timer a[0:1000000].avg();

Time elapsed: 8 ms
```

例3：`subarray` 返回的子向量是只读的。

```dolphindb
b=a.subarray(0:1000000);
b[0]=1;

Assignment statement failed probably due to invalid indices.
```
