---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getHaMvccTableInfo.html
fetched_at: 2026-05-19T09:23:55Z
category: funcs
title: getHaMvccTableInfo
sha1: 9f9012619a57092165f5343d4c314d137773d5e5
---

# getHaMvccTableInfo

首发版本：3.00.5

## 语法

`getHaMvccTableInfo(groupId)`

## 详情

获取指定 MVCC Raft 组内所有的元信息。

此函数必须在该 Raft 组的成员节点上执行。

## 参数

**groupId** 是一个整数，表示 HaMvcc 的 Raft 组 ID。

## 返回值

返回一个表，包含以下列（列名以实际系统输出为准）：

- `tableName`：STRING 类型，表示表名。
- `rows`：LONG 类型，表示行数。
- `memoryUsed`：LONG 类型，表示内存占用，单位为字节。
- `schema`：STRING 类型，表示表结构。
- `defaultValues`：STRING 类型，表示各列的默认值。
- `allowNull`：STRING 类型，表示各列是否允许值为 NULL。

## 例子

```dolphindb
getHaMvccTableInfo(5)
```

| tableName | rows | memoryUsed | schema | defaultValues | allowNull |
| --- | --- | --- | --- | --- | --- |
| demoHaMvcc | 10 | 640 | name:STRING, id:INT, value:DOUBLE | A001, 1, 3.6 | false, true, false |

**相关函数**：[haMvccTable](../h/haMvccTable.html)
