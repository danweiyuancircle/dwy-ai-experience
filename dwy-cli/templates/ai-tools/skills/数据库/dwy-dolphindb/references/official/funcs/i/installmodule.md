---
source_url: https://docs.dolphindb.cn/zh/funcs/i/installmodule.html
fetched_at: 2026-05-19T09:27:46Z
category: funcs
title: installModule
sha1: 99f7477fb30eadf77f62c0657da7620074e8b1cb
---

# installModule

首发版本：3.00.5，3.00.4.3

## 语法

`installModule(moduleName, [serverAddr])`

## 详情

下载并解压指定模块到节点的模块目录下。可通过 [listRemoteModules](../l/listremotemodules.html) 函数查询可供下载的模块。

## 参数

**moduleName** STRING 类型标量，用于指定模块名称。

**serverAddr** 可选参数，STRING 类型标量，用于指定模块仓库的 HTTP 地址。默认为 "http://dolphindb.cn" 。

## 返回值

无。

## 例子

从市场下载名为 ops 的模块：

```dolphindb
installModule("ops")
```

**相关函数**

[listRemoteModules](../l/listremotemodules.html)

[loadModule](../l/loadModule.html)
