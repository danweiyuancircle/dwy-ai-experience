---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/null_in_vst.html
fetched_at: 2026-05-19T09:02:32Z
category: progr
title: 向量/集合/元组中的空值
sha1: 339aca52130a81f3ee81ad812610160ecae64ed2
---

# 向量/集合/元组中的空值

含有空值的向量：

```dolphindb
x=1 2 NULL NULL 3;
y=2 NULL NULL 3 4;
x+y;
// output
[3,,,,7]

x*y;
// output
[2,,,,12]

x**y;
// output
14
// 内积

sum x;
// output
6

x<y;
// output
[1,0,0,1,1]

x||1;
// output
[1,1,,,1]

// 除了<, <=这些关系运算符之外，任何在空值上的二元操作将会得到空值。
```

含有空值的集合：

```dolphindb
a=set(1 NULL)
b=set(2 NULL);
x=a&b;
x;
// output
set(00i)

// x 和 y 的公共元素是 NULL
NULL in x;
// output
1
size(x);
// output
1

// 集合 x 不为空，因为有一个空值。
c=set(2 3);
y=a&c;
y;
// output
set()

size(y);
// output
0

// 测试一个集合是否为空的唯一方式是 size(y)==0
```

含有空值的元组：

```dolphindb
x=(1, NULL);
x+1;
// output
(2,)
```
