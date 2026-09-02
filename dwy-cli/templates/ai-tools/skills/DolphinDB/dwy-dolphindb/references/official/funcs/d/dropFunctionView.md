---
source_url: https://docs.dolphindb.cn/zh/funcs/d/dropFunctionView.html
fetched_at: 2026-05-19T09:19:22Z
category: funcs
title: dropFunctionView
sha1: 4a7d596915344694e8f818e3ad7f0698afeafa1a
---

# dropFunctionView

## 语法

`dropFunctionView(name,
[isNamespace=false])`

## 详情

删除一个视图或一个命名空间下的所有函数。

`dropFunctionView`只能由管理员或拥有 VIEW\_OWNER
权限的普通用户执行。

## 参数

**name** 是一个字符串标量，表示用户自定义函数名称或一个命名空间。

**isNamespace** 是一个布尔标量，指示 name 是否是一个命名空间。

## 返回值

无。

## 例子

```dolphindb
getFunctionViews()
name      body                           
--------- ------------------
f1        def f1(){return 1}
test::f1 def f1(){return 2}
test::f2 def f2(){return 3}

// 删除 f1
dropFunctionView(`f1)
// 删除 test::f1
dropFunctionView("test::f1")
// 删除命名空间 test 下所有函数
dropFunctionView("test",true)
```
