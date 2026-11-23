---
source_url: https://docs.dolphindb.cn/zh/progr/data_types_forms/Pair.html
fetched_at: 2026-05-19T09:00:29Z
category: progr
title: 数据对
sha1: 460edfb0297ff23295f8eb49155f627bc85d0e5a
---

# 数据对

## 概述

数据对是只有两个值的特殊的向量。一个数据对包含了两个标量值。这两个标量值必须满足以下任一条件：

- 它们的数据类型相同。
- 它们都属于 INTEGRAL、FLOATING 或 DECIMAL 类别。

数据对类型的数据可用于：

1. **代表数据范围**

   不包含上限的数据范围有以下几种情况：

   1. 表示索引：

      ```dolphindb
      x=5 3 6 2;
      x[1:3];
      // output
      [3,6]
      a=rand(1000.0,20000000)
      b=a.subarray(0:1000000);
      m=matrix(1 2 3 4, 5 6 7 8, 9 10 11 12);
      m;
      ```

      | #0 | #1 | #2 |
      | --- | --- | --- |
      | 1 | 5 | 9 |
      | 2 | 6 | 10 |
      | 3 | 7 | 11 |
      | 4 | 8 | 12 |

      ```dolphindb
      m[1:2, 0:2];
      ```

      | #0 | #1 |
      | --- | --- |
      | 2 | 6 |
   2. 表示 for-loop
      的范围：

      ```dolphindb
      for(s in 1:3){print s};
      // output
      1
      2
      ```
   3. 在 [bucket](../../funcs/b/bucket.html) 或 [bucketCount](../../funcs/b/bucketCount.html)
      函数中：

      ```dolphindb
      bucket(4 0 1 3 2, 0:4, 2);
      // output
      [,0,0,1,1]
      ```

   其它情况下，数据范围均包含上限。

   ```dolphindb
   [5,6,8] between 1:6;
   // output
   [1,1,0]

   t1 = table(`A`A`B as sym, 09:56:06 09:56:07 09:56:06 as time, 10.6 10.7 20.6 as price)
   t2 = table(take(`A,10) join take(`B,10) as sym, take(09:56:00+1..10,20) as time, (10+(1..10)\10-0.05) join (20+(1..10)\10-0.05) as bid, (10+(1..10)\10+0.05) join (20+(1..10)\10+0.05) as offer, take(100 300 800 200 600, 20) as volume)
   wj(t1, t2, -5:0, <avg(bid)>, `sym`time);
   ```
2. 表示矩阵的维度。例如，"2:5" 表示一个 2 乘 5 的矩阵。如果一个一维数组 x 有 10 个元素，x$2:5 表示把 x 转化为 2 乘 5
   的矩阵，其中“$”表示转化。
3. 创建 [table](../../funcs/t/table.html)
   时指定容量和初始行数。

   ```dolphindb
   t=table(100:0, `date`sym`high`low`close, [DATE,SYMBOL,DOUBLE,DOUBLE,DOUBLE]);
   ```

## 创建数据对

使用冒号 ":" 或 [pair](../../funcs/p/pair.html)
函数来创建数据对数据。

例如：

```dolphindb
1:3;
3.4:7.8;
1b:0b;

# 返回：
1:0

true:false;

# 返回：
1:0

2013.06.13:2013.11.10;
5 pair 6;

# 返回：
5:6

`Hello:`World;
# 返回：
"Hello" : "World"
```

## 访问数据对

用 X[Y] 的形式访问数据对数据。Y 可以是整数也可以是整数向量，或者数据对。例如：

```dolphindb
x = 3:6;
x[1];
```

返回：6

```dolphindb
x[0 1];
```

返回：[3,6]

## 修改数据对

数据对中的两个值可以分别被修改。例如：

```dolphindb
x=3:6;
x[0]=4;
x;
```

返回：4:6

```dolphindb
x=3:6+1;
x;
```

返回：4:7
