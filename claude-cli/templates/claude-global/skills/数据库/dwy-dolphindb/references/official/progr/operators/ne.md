---
source_url: https://docs.dolphindb.cn/zh/progr/operators/ne.html
fetched_at: 2026-05-19T09:01:23Z
category: progr
title: ne(!= or <>)
sha1: 08fc1f32d7b6cc0adba24e008ff364b3fc800e1b
---

# ne(!= or <>)

## 语法

X != Y 或 X<>Y

## 参数

**X** 和 **Y** 可以是标量、数据对、向量、矩阵或集合。当 *X* 和 *Y*
都是向量或矩阵时，它们的长度或维度必须相同。

## 详情

如果X和Y都不是集合，对X和Y中的元素逐个比较; 如果X和Y中的元素不相同，则返回1。

如果X和Y是集合，则检查X和Y是否不相同。

## 例子

```dolphindb
1 2 3 != 2;
// output
[true,false,true]

1 2 3 ne 0 2 4;
// output
[true,false,true]

1:2 != 1:6;
// output
[false,true]

m1=1..6$2:3;
```

```dolphindb
m1 != 4;
```

```dolphindb
m1;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 3 | 5 |
| 2 | 4 | 6 |

| #0 | #1 | #2 |
| --- | --- | --- |
| true | true | true |
| true | false | true |

```dolphindb
m2=6..1$2:3;
m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 6 | 4 | 2 |
| 5 | 3 | 1 |

```dolphindb
m1 ne m2;
```

| #0 | #1 | #2 |
| --- | --- | --- |
| true | true | true |
| true | true | true |

```dolphindb
t = table(`A`B`M`B`A`M as sym, 10.1 11.2 11.3 12 10.6 10.8 as val)
select * from t where nullIf(sym, `M)<>NULL
```

表 1.

| sym | val |
| --- | --- |
| A | 10.1 |
| B | 11.2 |
| B | 12 |
| A | 10.6 |

提示：

在集合操作中，如果 X!=Y，则 X 和 Y 不是同一个集合。

```dolphindb
x=set(4 6);
y=set(4 6 8);

x!=y;
// output
true
x!=x;
// output
false
1 2 3 != 2
[true,false,true]
```
