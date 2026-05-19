---
source_url: https://docs.dolphindb.cn/zh/progr/sql/isnull.html
fetched_at: 2026-05-19T09:03:45Z
category: progr
title: is null
sha1: 4407545beb42b31843b7392035502f59540d7db3
---

# is null

## 用法

- is null 谓词用于检测空值，其功能等价于 isNull 函数。
- is not null 谓词用于检测非空值。

**注意**：支持在分布式查询中使用。

## 例子

```dolphindb
t= table(`a1`a2`a3`b1`b2`b3`c1`c2 as id, 7 4 NULL 1 8 NULL 12 NULL as val)
select id from t where val is null 
// 等价于 select id from t where isNull(val)
```

| id |
| --- |
| a3 |
| b3 |
| c2 |

```dolphindb
select id from t where  val  is not null
// 等价于 select id from t where not isNull(val)
```

| id |
| --- |
| a1 |
| a2 |
| b1 |
| b2 |
| c1 |
