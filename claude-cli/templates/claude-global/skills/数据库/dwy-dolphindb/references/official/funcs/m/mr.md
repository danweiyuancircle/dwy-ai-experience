---
source_url: https://docs.dolphindb.cn/zh/funcs/m/mr.html
fetched_at: 2026-05-19T09:32:34Z
category: funcs
title: mr
sha1: 710ac2a9e98bca4fc475ee27b529f848030686b6
---

# mr

## 语法

`mr(ds, mapFunc, [reduceFunc], [finalFunc], [parallel=true])`

## 详情

`mr` 是 DolphinDB 中执行 MapReduce 计算的通用函数。 当数据分布在多个数据源上时，可以先对每个数据源分别计算，再把各部分结果合并，最后按需要做一次统一处理。

### 什么是 MapReduce

可以把 MapReduce 理解成**两个核心阶段**，更详细的介绍请参考[什么是 MapReduce](https://www.ibm.com/cn-zh/think/topics/mapreduce)：

1. map：对每个数据源分别执行同一段计算逻辑。
2. reduce：把多个 map 结果逐步合并成一个结果。

注：

除了以上两个核心阶段，`mr` 函数还支持第三阶段（final），即通过
*finalFunc* 参数对合并后的结果做最后加工，得到真正想要的输出。

### 适用场景

- 数据分散在多个数据源中，如多个分区或多个表；
- 每份数据都可以先独立计算，再统一汇总；
- 单个数据源上的计算逻辑相同；
- 希望利用并行计算提升处理效率。

## 参数

**ds** 数据源列表，必须是一个元组，元组的每个元素都是[数据源对象](https://docs.dolphindb.cn/zh/tutorials/general_computing.html#ariaid-title6)。 即使只有一个数据源，也需要写成元组形式。

**mapFunc** 针对每个数据源的计算函数（即 map 函数）。 它只接收一个参数，即“从当前数据源列表中提取出来、可供计算的数据对象”。
如果计算函数本身包含多个参数，可以使用[部分应用](../../progr/partial_app.html)将其转换为仅接收一个参数的函数，并将该函数作为 map 函数传给 *mapFunc*。map
函数调用的次数等于数据源的数量，其返回值为一个常规对象（标量，数据对，向量，矩阵，表，集合或字典）或一个元组（包含多个常规对象）。

**reduceFunc** 可选，一个二元函数（即 reduce 函数），用于合并两个返回值。 这里的两个返回值，可能都来自 map 函数，也可能其中一个是前一个
reduce 函数的返回值。 系统会把上一步的合并结果继续与下一个 map 函数的返回值合并，直到所有 map 函数的返回值都被合并完。

**finalFunc** 可选，用于生成最终输出的函数。 它只接收一个参数，即最后一次调用 reduce 函数的输出。 如果没有指定 reduce 函数但指定了 final 函数，系统先将所有 map 函数的结果合并成一个元组，然后将元组作为输入来调用 final 函数。

**parallel** 可选，是否并行执行 map 函数，默认值为 true。 一般情况下，开启并行可以提升计算速度，但在以下情况可以考虑设为 false：

- 单次 map 计算非常占内存；
- 多个线程并发执行时可能引发线程安全问题； 例如，如果多个线程同时写入同一个文件，则可能会发生错误。

## 返回值

- 如果指定了 *finalFunc*，返回 *finalFunc* 的结果；
- 如果没有指定 *finalFunc*，但指定了 *reduceFunc*，返回 *reduceFunc* 的最终结果；
- 如果两者都没有指定，返回所有 *mapFunc* 的汇总结果，形式为一个元组。

## 例子

例 1：计算多个分区中的全局均值和方差。

```dolphindb
// 创建 catalog，并切换到该 catalog
createCatalog("demo")
go
use catalog demo
// 在当前 catalog 下创建分布式数据库和分区表
create database mr_demo partitioned by VALUE(2024.01.01 2024.01.02 2024.01.03), engine='OLAP'
go
create table mr_demo.pt (
    date DATE,
    id INT,
    value DOUBLE
)
partitioned by date

// 写入测试数据
data = table(
    2024.01.01 2024.01.01 2024.01.01 2024.01.02 2024.01.02 2024.01.03 2024.01.03 as date,
    1 2 3 4 5 6 7 as id,
    10.0 20.0 30.0 40.0 50.0 60.0 70.0 as value
)
demo.mr_demo.pt.append!(data)

// 用 sqlDS 把查询转换成数据源列表
ds = sqlDS(<select * from mr_demo.pt>)

// map：在每个分区中计算局部统计量
def statsMap(table){
    x = table.value // 取表格 value 列的值
    return [x.size(), sum(x), sum(pow(x, 2.0))] // 计算行数、值的总和、值的平方和
}

// reduce：把两个局部统计量逐项相加
def statsReduce(x, y){
    return [x[0] + y[0], x[1] + y[1], x[2] + y[2]]
}

// final：根据汇总统计量计算全局均值和方差
def statsFinal(result){
    count = result[0]
    totalSum = result[1]
    totalSquares = result[2]
    avg = totalSum / count
    variance = totalSquares / count - avg * avg
    return table(avg as mean, variance as variance)
}

// 调用 mr
result = mr(ds, statsMap, statsReduce, statsFinal)

// 查看结果
result
```

输出如下：

| mean | variance |
| --- | --- |
| 40 | 400 |

例 2：在多个数据源上计算最小二乘线性回归的结果。

线性回归用于根据一个或多个自变量预测因变量。 若记因变量为 y，自变量矩阵为 X，则最小二乘法的目标是求出回归系数 beta，计算公式如下：

```dolphindb
beta = (X^T X)^(-1) X^T y
```

因此，完成回归计算的关键在于先得到整个数据集的 X^T X 和 X^T y。 当数据分布在多个数据源上时，可以先在每个数据源上计算局部的 Xi^T Xi 和 Xi^T yi，再将它们汇总为全局结果。 示例代码：

```dolphindb
def myOLSMap(table, yColName, xColNames, intercept){
  if(intercept)
      x = matrix(take(1.0, table.rows()), table[xColNames])
  else
      x = matrix(table[xColNames])
  xt = x.transpose();
  return xt.dot(x), xt.dot(table[yColName])
}

def myOLSFinal(result){
  xtx = result[0]
  xty = result[1]
  return xtx.inv().dot(xty)[0]
}

def myOLSEx(ds, yColName, xColNames, intercept){
  return mr(ds, myOLSMap{, yColName, xColNames, intercept}, +, myOLSFinal)
}
```

- **map**：`myOLSMap` 用于对单个数据源执行局部计算。 其输入包括：
  - *table*：当前数据源对应的数据表
  - *yColName*：因变量列名
  - *xColNames*：自变量列名
  - *intercept*：指定是否包含截距项

  该函数首先构造局部自变量矩阵 Xi，然后返回当前数据源的局部统计量：Xi^T Xi 和 Xi^T yi。
- **reduce**：`+` 作为 reduce 函数，将各单个数据源的计算结果逐项相加。
  - 例如两个分区分别返回：(X1^T X1, X1^T y1) 和 (X2^T X2, X2^T y2)，那么 reduce 后得到 (X1^T
    X1 + X2^T X2, X1^T y1 + X2^T y2)；
  - 继续和下一个分区结果合并后，最终得到全局的 (X^T X, X^T y)。
- **final**：`myOLSFinal` 用于处理 reduce 阶段的汇总结果，即根据最小二乘公式求出回归系数。
  - *xtx* 表示汇总后的 X^T X；
  - *xty* 表示汇总后的 X^T y；
  - `xtx.inv()` 表示对矩阵 *xtx* 求逆；
  - `xtx.inv().dot(xty)` 表示做矩阵乘法，对应公式 `(X^T X)^(-1)
    X^T y`。
- `myOLSEx` 用于封装 `mr` 函数，执行 map → reduce → final
  的计算逻辑。

注：

作为经常使用的分析工具，分布式最小二乘线性回归已经在内置函数 [olsEx](https://docs.dolphindb.cn/zh/funcs/o/olsEx.html) 中实现。
