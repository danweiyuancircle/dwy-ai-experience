---
source_url: https://docs.dolphindb.cn/zh/funcs/t/toArray.html
fetched_at: 2026-05-19T09:42:30Z
category: funcs
title: toArray
sha1: 117c4b7a86431b28b777a3d8865cf7e7a7c53c74
---

# toArray

## 语法

`toArray(X)`

## 详情

与 [group by](../../progr/sql/groupby.html) 搭配使用，按照分组将 *X*
转换为[数组向量（array
vector）](../../progr/data_types_forms/arrayVector.html)。如果单独使用则没有效果。

## 参数

**X** 是表的列字段名称或包含列字段的计算表达式。

## 返回值

数据类型同 *X* 的数组向量。

## 例子

```dolphindb
t = table(1 1 3 4 as id, 1 3 5 6 as v1)
new_t = select toArray(v1) as newV1 from t group by id
/* 
id newV1
-- -----
1  [1,3]
3  [5]  
4  [6]  
*/

new_t = select toArray(v1+1) as newV1 from t group by id
/* 
id newV1
-- -----
1  [2,4]
3  [6]  
4  [7]  
*/
```

**相关函数：**[toColumnarTuple](tocolumnartuple.html), [toTuple](totuple.html)。
