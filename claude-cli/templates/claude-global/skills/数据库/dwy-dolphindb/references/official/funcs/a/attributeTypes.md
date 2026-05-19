---
source_url: https://docs.dolphindb.cn/zh/funcs/a/attributeTypes.html
fetched_at: 2026-05-19T09:13:27Z
category: funcs
title: attributeTypes
sha1: 6a0acb239cfdb6b17d26c9653cfe19734e9bf306
---

# attributeTypes

首发版本：3.00.4.2，3.00.3.2

## 语法

`attributeTypes(obj)`

## 参数

**obj** 类实例。

## 详情

获取类或类实例中所有属性及其对应的类型。

## 返回值

一个表，包含如下列：

- attr：属性名称。
- type：数据类型。

## 例子

```dolphindb
class Person {
	name :: STRING
	age :: INT
	def Person(name_, age_) { 
		name = name_
		age = age_
	}
}
p1 = Person("Sam", 12)
attributeTypes(p1)  // 或者 attributeTypes(Person)
```

| attr | type |
| --- | --- |
| name | STRING |
| age | INT |

**相关函数**：[attributeNames](attributenames.html)、[attributeValues](attributevalues.html)
