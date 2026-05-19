---
source_url: https://docs.dolphindb.cn/zh/funcs/a/attributenames.html
fetched_at: 2026-05-19T09:13:26Z
category: funcs
title: attributeNames
sha1: dc8fbfa794800cad9b2384b88ce5d0e5706ede94
---

# attributeNames

## 语法

`attributeNames(obj)`

## 详情

获取类实例的所有属性名称。

## 参数

**obj** 类实例。

## 返回值

字符串向量

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

p = Person("Sam", 12)
attributeNames(p)

// output: ["name","age"]
```
