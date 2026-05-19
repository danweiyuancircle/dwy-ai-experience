---
source_url: https://docs.dolphindb.cn/zh/funcs/e/erase_.html
fetched_at: 2026-05-19T09:21:07Z
category: funcs
title: erase!
sha1: e893aa6287a13b003000368bb46f225a18fb3224
---

# erase!

## 语法

`erase!(obj, key|filter)`

## 详情

删除集合中的某些元素或字典中的键值或表中的某些行。

## 参数

**obj** 可以是集合、字典或表。

对于集合，**key|filter** 表示要删除的元素；对于字典，*key|filter*
表示要删除的键值；对于表，*key|filter* 表示过滤条件的元代码。

## 返回值

返回修改后的集合、字典或表，数据类型同 *obj*。

## 例子

对于集合：

```dolphindb
y=set(8 9 4 6);
y;
// output
set(6,4,9,8)
y.erase!(6);
// output
set(4,9,8)
erase!(y, 9 8);
// output
set(4)
```

对于字典：

```dolphindb
x=1..6;
y=11..16;
z=dict(x,y);
z;
// output
6->16
5->15
4->14
3->13
2->12
1->11

erase!(z, 1..4);
// output
6->16
5->15
```

对于表：

```dolphindb
x=1..10;
y=11..20;
t=table(x,y);
// output
erase!(t, <x<=3>);
```

| x | y |
| --- | --- |
| 4 | 14 |
| 5 | 15 |
| 6 | 16 |
| 7 | 17 |
| 8 | 18 |
| 9 | 19 |
| 10 | 20 |

```dolphindb
erase!(t, <x<=9 and y>=15>);
```

| x | y |
| --- | --- |
| 4 | 14 |
| 10 | 20 |
