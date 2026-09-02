---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dynamicGroupCumcount.html
fetched_at: 2026-05-19T09:20:30Z
category: funcs
title: dynamicGroupCumcount
sha1: f4171d413529a787b68578f5462bf866ec48a385
---

# dynamicGroupCumcount

## 语法

`dynamicGroupCumcount(membership, prevMembership, groupCount)`

## 详情

通常一个事件的类别和属性是固定的。但在某些场景下，事件的类别会动态发生变化。如：在实时处理逐笔数据时，进行大小单的统计以对资金流进行分析。用户期望根据某个订单（事件的属性）的累计交易量来判断该订单是大单还是小单（事件的类别）。随着实时数据不断流入，交易量的不断增加，该订单的类别可能从一个小单变成大单。

`dynamicGroupCumcount`
即可应用在这类场景下，用于统计在一个时间序列下，不同类别的累计事件数。

具体算法如下：

- 若 *membership* = *prevMembership*，统计量不变。
- 若 *membership* ≠ *prevMembership*，*membership*
  对应组的统计量加1，*prevMembership* 对应的组统计量减1。
- 若 *prevMembership* 为空值（对应序列的第一条记录），*membership*
  对应组的统计量加1，*prevMembership* 无对应组，无需处理。

## 参数

**membership** 整型向量，其元素必须是 [0, groupCount) 范围内的整数。用于记录事件在每个时间戳上对应的标签。

**prevMembership** 整型向量，其元素可以为空值（对应序列的第一条记录）。用于记录事件在前一个时间戳上对应的标签。

**groupCount** [2, 8] 之间的一个整数。表示函数返回值（元组）的长度，即需要统计的标签数。

## 返回值

返回一个长度为 *groupCount* 的元组，其每个元素是一个与 *membership* 等长的向量，依次记录了各标签统计的累积记录数。

注：

元组的下标与标签号一一对应，即标签为 0 的统计结果将输出至元组下标为 0 的向量。

## 例子

数据预处理：

```dolphindb
# 打标签函数
def tag_func(v){

  return iif(v <= 5, 0, iif(v <= 10 and v > 5, 1, 2))
// output
}
# 原始数据表
time = take(2022.01.01T09:00:00.000 + 1..3, 6)
sym=`st0`st0`st0`st1`st1`st1
orderNo = `10001`10002`10001`10002`10003`10002
volume = 2 4 6 3 2 9
t = table(sym, time, orderNo, volume)

# 计算累计和并根据阈值打标签
t1 = select *, cumsum(volume) as sumVolume from t context by sym, orderNo
t2 = lj(t, t1,`sym`time`orderNo)
t3 = select sym, time, orderNo, volume, sumVolume, tag_func(sumVolume) as groupId from t2
```

对于历史数据，可以使用 SQL 语句计算不同组的累计记录数：

```dolphindb
t4 = select sym, time, orderNo, prev(groupId) as prevGroupId from t3 context by sym,orderNo
t5 = lj(t3, t4,`sym`time`orderNo)
re = select sym, time, orderNo, dynamicGroupCumcount(groupId, prevGroupId, 3) as `groupId0`groupId1`groupId2 from t5 context by sym
re
```

| sym | time | orderNo | groupId0 | groupId1 | groupId2 |
| --- | --- | --- | --- | --- | --- |
| st0 | 2022.01.01T09:00:00.001 | 10001 | 1 | 0 | 0 |
| st0 | 2022.01.01T09:00:00.002 | 10002 | 2 | 0 | 0 |
| st0 | 2022.01.01T09:00:00.003 | 10001 | 1 | 1 | 0 |
| st1 | 2022.01.01T09:00:00.001 | 10002 | 1 | 0 | 0 |
| st1 | 2022.01.01T09:00:00.002 | 10003 | 2 | 0 | 0 |
| st1 | 2022.01.01T09:00:00.003 | 10002 | 1 | 0 | 1 |

对于实时数据，可以使用流数据引擎计算不同组的累计记录数：

```dolphindb
result = table(1000:0, `sym`time`orderNo`groupId0`groupId1`groupId2, [SYMBOL, TIME, SYMBOL,INT,INT,INT])
factor0 = [<time>,  <prev(groupId) as prevGroupId>, <groupId>, <volume>]
factor1 = [<time>, <orderNo>, <dynamicGroupCumcount(groupId, prevGroupId, 3)>]
dm1 = table(1000:0, `sym`time`orderNo`volume`sumVolume`groupId, [SYMBOL, TIME, SYMBOL,INT, INT,INT])
dm2 = table(1000:0, `sym`orderNo`time`prevGroupId`groupId`volume, [SYMBOL, SYMBOL, TIME, INT,INT,INT])
res1 = createReactiveStateEngine(name="reactive_ccnt", metrics =factor1, dummyTable=dm2, outputTable=result, keyColumn=`sym, keepOrder=true)
res0 = createReactiveStateEngine(name="reactive_prev", metrics =factor0, dummyTable=dm1, outputTable=res1, keyColumn=`sym`orderNo, keepOrder=true)
res0.append!(t3)

select * from result
```

| sym | time | orderNo | groupId0 | groupId1 | groupId2 |
| --- | --- | --- | --- | --- | --- |
| st0 | 2022.01.01T09:00:00.001 | 10001 | 1 | 0 | 0 |
| st0 | 2022.01.01T09:00:00.002 | 10002 | 2 | 0 | 0 |
| st0 | 2022.01.01T09:00:00.003 | 10001 | 1 | 1 | 0 |
| st1 | 2022.01.01T09:00:00.001 | 10002 | 1 | 0 | 0 |
| st1 | 2022.01.01T09:00:00.002 | 10003 | 2 | 0 | 0 |
| st1 | 2022.01.01T09:00:00.003 | 10002 | 1 | 0 | 1 |

```dolphindb
dropStreamEngine("reactive_ccnt")
dropStreamEngine("reactive_prev")
```

相关函数：[dynamicGroupCumsum](dynamicGroupCumsum.html)
