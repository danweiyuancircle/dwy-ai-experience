---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setSystem.html
fetched_at: 2026-05-19T09:39:06Z
category: funcs
title: setSystem
sha1: b3c8699c9ffefd59560b3ab28c665c620e681c19
---

# setSystem

## 语法

`setSystem(paramName, paramValue)`

## 详情

`setSystem` 用于设置以下的系统级参数：

- 在命令行窗口显示的对象的最大行数
- 在命令行窗口显示的对象的最大行宽

只有管理员有权限执行 `setSystem` 命令。

## 参数

**paramName** 是参数名，**paramValue** 是对应的参数值。

## 例子

```dolphindb
setSystem("rows", 30);
setSystem("width", 200);
```
