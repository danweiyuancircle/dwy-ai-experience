---
source_url: https://docs.dolphindb.cn/zh/funcs/c/ceil.html
fetched_at: 2026-05-19T09:14:51Z
category: funcs
title: ceil
sha1: ecb2ed8af704d52c17e4f7c1830404606dda211f
---

# ceil

## 语法

`ceil(X)`

## 详情

函数 [floor](../f/floor.html) 和 `ceil`
分别把一个实数映射到小于等于它的最大整数，和大于等于它的最小整数。函数 [round](../r/round.html)
根据四舍五入规则把一个实数映射到最接近的整数。

注：

与 [numpy.ceil](https://numpy.org/doc/stable/reference/generated/numpy.ceil.html) 函数的核心功能相同，区别在于 DolphinDB 中的
`ceil` 函数只接受一个参数 *X*，不支持 `numpy.ceil` 中的
*out*、*where*、*dtype*、*casting* 和 *order* 等参数。

## 参数

**X** 可以是标量、向量或矩阵。

## 返回值

整数类型标量、向量或矩阵。

## 例子

```dolphindb
ceil(2.1);
// output
3
ceil(2.9);
// output
3
ceil(-2.1);
// output
-2

floor(2.1);
// output
2
floor(2.9);
// output
2
floor(-2.1);
// output
-3

round(2.1);
// output
2
round(2.9);
// output
3
round(-2.1);
// output
-2

m = 1.1 2.2 3.3 4.4 5.5 6.6 7.7 8.8 9.9 10$2:5;
m;
```

| 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| 1.1 | 3.3 | 5.5 | 7.7 | 9.9 |
| 2.2 | 4.4 | 6.6 | 8.8 | 10 |

```dolphindb
ceil(m);
```

| 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| 2 | 4 | 6 | 8 | 10 |
| 3 | 5 | 7 | 9 | 10 |
