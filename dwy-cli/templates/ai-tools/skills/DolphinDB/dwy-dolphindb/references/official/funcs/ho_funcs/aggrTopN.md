---
source_url: https://docs.dolphindb.cn/zh/funcs/ho_funcs/aggrTopN.html
fetched_at: 2026-05-19T09:44:45Z
category: funcs
title: aggrTopN
sha1: 57444b11dafff64de6375f14318de38930911b7b
---

# aggrTopN

## 语法

`aggrTopN(func, funcArgs, sortingCol, top, [ascending=true])`

## 详情

将 *sortingCol* 根据 *ascending* 指定方式进行排序后，得到
*funcArgs* 中对应的前 *top* 个元素，使用 *func*
指定的聚合函数进行计算。*sortingCol* 包含的 NULL 值当作最小值处理。

## 参数

- **func** 必须是一个聚合函数。
- **funcArgs** 是 *func* 的参数，可以是标量或向量。 *func* 有多个参数时，它是一个元组。
- **sortingCol** 是一个数值类型或时间类型的向量，提供 *funcArgs* 的排序指标。
- **top** 可以是整数或者浮点数。

  - 如果是整数，表示选取的前 *top* 行数据；
  - 如果是浮点数，表示百分比，必须小于1.0。根据 *funcArgs*
    的总行数\**top* 来确定需要选取的行数。若结果不是整数，则向下取整，至少取一行。
- **ascending** 是一个布尔值，表示是否按升序排序。 默认值是 true。

其他相关 TopN 系列函数参数说明和窗口计算规则请参考: [TopN](../themes/TopN.html)

## 返回值

一个数值型标量。

## 例子

**例 1** 计算 volume 最大的 3 条数据对应 price 的平均值。

```dolphindb
price = 10.0 20.0 30.0 40.0 50.0
volume = 5 2 5 1 4
aggrTopN(func=avg, funcArgs=price, sortingCol=volume, top=3, ascending=false)
// output:30
```

**例 2** 计算 volume 最大的 3 条数据 price 和 volume 的相关性，此时 *func*
为双目聚合函数，*funcArgs* 需传入元组。

```dolphindb
volume=2 3 4 5 3
price=10.0 20.0 30.0 40.0 50.0
aggrTopN(func=corr, funcArgs=(volume, price), sortingCol=2 3 4 5 3, top=3, ascending=true)
// output:0.69338
```

**例 3** 计算 volume 最大的 N 条数据对应 price 的平均值。N 可通过指定 *top* 为整数
N，或为浮点数表示比例。

```dolphindb
price = 10 20 30 40 50
volume = 1 2 3 4 5
// top=3 整数：取前 3 行
aggrTopN(func=avg, funcArgs=price, sortingCol=volume, top=3)
// 取[10,20,30], output: 20

// top=0.6 浮点数：取前 floor(5*0.6)=3 行
aggrTopN(func=avg, funcArgs=price, sortingCol=volume, top=0.6)
// 取[10,20,30], output: 20

// top=0.5 浮点数：取前 floor(5*0.5)=2 行，此处向下取整
aggrTopN(func=avg, funcArgs=price, sortingCol=volume, top=0.5)
// 取[10,20], output: 15

// top=0.01 浮点数：5*0.01=0.05 向下取整为 0，但保底至少取 1 行                                                   
aggrTopN(func=sum, funcArgs=price, sortingCol=volume, top=0.01)                                        
// 取[10], output: 10
```

**例 4** 统计每天每只股票因子最小的 40% 的 value 的平均值。

```dolphindb
trade_date=sort(take(2017.01.11..2017.01.12,20))
secu_code=take(`600570`600000,20)
value=1..20
tb=table(trade_date,secu_code,value)
```

| trade\_date | secu\_code | value |
| --- | --- | --- |
| 2017.01.11 | 600570 | 1 |
| 2017.01.11 | 600000 | 2 |
| 2017.01.11 | 600570 | 3 |
| 2017.01.11 | 600000 | 4 |
| 2017.01.11 | 600570 | 5 |
| 2017.01.11 | 600000 | 6 |
| 2017.01.11 | 600570 | 7 |
| 2017.01.11 | 600000 | 8 |
| 2017.01.11 | 600570 | 9 |
| 2017.01.11 | 600000 | 10 |
| 2017.01.12 | 600570 | 11 |
| 2017.01.12 | 600000 | 12 |
| 2017.01.12 | 600570 | 13 |
| 2017.01.12 | 600000 | 14 |
| 2017.01.12 | 600570 | 15 |
| 2017.01.12 | 600000 | 16 |
| 2017.01.12 | 600570 | 17 |
| 2017.01.12 | 600000 | 18 |
| 2017.01.12 | 600570 | 19 |
| 2017.01.12 | 600000 | 20 |

```dolphindb
select aggrTopN(avg, funcArgs=value, sortingCol=value, top=0.4, ascending=true) as factor_value from tb group by trade_date,secu_code
```

| trade\_date | secu\_code | factor\_value |
| --- | --- | --- |
| 2017.01.11 | 600000 | 3 |
| 2017.01.11 | 600570 | 2 |
| 2017.01.12 | 600000 | 13 |
| 2017.01.12 | 600570 | 12 |
