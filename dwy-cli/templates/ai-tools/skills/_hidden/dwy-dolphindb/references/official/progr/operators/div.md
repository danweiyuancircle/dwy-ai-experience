---
source_url: https://docs.dolphindb.cn/zh/progr/operators/div.html
fetched_at: 2026-05-19T09:01:08Z
category: progr
title: div(/)
sha1: 1689f08bf3966c8fa69c957197048d701f591fd8
---

# div(/)

## 语法

`X/Y`

## 参数

**X** 和 **Y** 可以是标量、数据对、向量或矩阵。当X和Y都是向量或矩阵时，它们的长度或维度必须相同。

## 详情

把X的每一个元素除以Y后返回。当X和Y为float或double类型时，返回的结果是float或double类型。当X和Y均为整数时，div表示整数除法，与做除法后再用函数
[floor](../../funcs/f/floor.html) 一样。例如，5/2结果为2。如果要对整数做真正的除法，则可以使用运算符 [ratio](../../funcs/r/ratio.html)
""。

整数除法通常与运算符 [mod](../../funcs/m/mod.html) 一起用于分组数据。div和mod的结果应满足关系：X=div(X,Y)\*Y+mod(X,Y)。

## 例子

```dolphindb
9/2:5;
// output
4 : 1
```

```dolphindb
11:25/3:4;
// output
3 : 6
```

```dolphindb
x=1 2 3;
x/2;
// output
[0,1,1]
```

```dolphindb
2/x;
// output
[2,1,0]
```

```dolphindb
y=4 5 6;
x/y;
// output
[0,0,0]
```

```dolphindb
y/x;
// output
[4,2,2]
```

```dolphindb
m1=1..6$2:3;
m1;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

```dolphindb
m1/2;
```

返回：

| #0 | #1 | #2 |
| --- | --- | --- |
| 0 | 1 | 2 |
| 1 | 2 | 3 |

```dolphindb
m2=6..1$2:3;
m2;
```

返回：

| #0 | #1 | #2 |
| --- | --- | --- |
| 6 | 4 | 2 |
| 5 | 3 | 1 |

```dolphindb
m1/m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 0 | 0 | 2 |
| 0 | 1 | 6 |

```dolphindb
-7/5;
```

返回：-2

```dolphindb
x=-1 2 6;
x/-5;
```

返回：[0,-1,-2]
