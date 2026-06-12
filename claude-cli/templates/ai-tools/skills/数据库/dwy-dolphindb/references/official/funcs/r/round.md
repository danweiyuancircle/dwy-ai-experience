---
source_url: https://docs.dolphindb.cn/zh/funcs/r/round.html
fetched_at: 2026-05-19T09:36:40Z
category: funcs
title: round
sha1: 3cad51e22a126e4e2656dcfffe54086f7598e6f3
---

# round

## 语法

`round(X, [precision])`

## 详情

`round` 函数按照指定小数位数对 *X* 进行四舍五入运算。

[floor](../f/floor.html) 和 [ceil](../c/ceil.html) 函数分别将一个实数映射到不大于 *X* 的最大整数和不小于 *X*
的最小整数。

DolphinDB 的 `round` 按“四舍五入”处理；Python 内置 `round` 和
`numpy.round` 采用 half-to-even 规则。另外，DolphinDB 中
`round` 的参数 *precision* 范围是 0..10；Python 内置
`round` 的参数 *ndigits* 和 `numpy.round` 的参数
*decimals* 支持负数。

## 参数

**X** 可以是标量、向量或矩阵。

**precision** 是 0 到 10 的整数，表示保留小数点后几位。默认值是 0。

## 返回值

- *precision* 未指定或设置为0时，返回值数据类型为 LONG，数据形式同 *X*。
- *precision* 指定为大于0小于等于10的值时，返回值数据类型为 DOUBLE，数据形式同 *X*。

## 例子

```dolphindb
round 2.1;
//output: 2

round 2.9;
//output: 3

round -2.1;
//output: -2

round(2.154,2);
//output: 2.15

round(2.156,2);
//output: 2.16

ceil 2.1;
//output: 3

ceil 2.9;
//output: 3

ceil -2.1;
//output: -2

floor 2.1;
//output: 2

floor 2.9;
//output: 2

floor -2.1;
//output: -3

m = 1.1 2.2 3.3 4.4 5.5 6.6 7.7 8.8 9.9 10$2:5;
m;
```

返回：

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1.1 | 3.3 | 5.5 | 7.7 | 9.9 |
| 2.2 | 4.4 | 6.6 | 8.8 | 10 |

```dolphindb
round m;
```

返回：

| #0 | #1 | #2 | #3 | #4 |
| --- | --- | --- | --- | --- |
| 1 | 3 | 6 | 8 | 10 |
| 2 | 4 | 7 | 9 | 10 |
