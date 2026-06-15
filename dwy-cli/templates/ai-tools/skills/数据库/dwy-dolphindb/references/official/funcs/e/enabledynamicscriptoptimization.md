---
source_url: https://docs.dolphindb.cn/zh/funcs/e/enabledynamicscriptoptimization.html
fetched_at: 2026-05-19T09:20:40Z
category: funcs
title: enableDynamicScriptOptimization
sha1: 130bde4f47353caadf3c4ccbaf3d8b88e2ef0e25
---

# enableDynamicScriptOptimization

## 语法

`enableDynamicScriptOptimization()`

## 详情

开启脚本引擎优化。

此命令须在控制节点由管理员执行。

此命令的影响将在系统重启后失效。若要永久生效，请在配置文件（集群模式为 controller.cfg，单节点模式为 dolphindb.cfg）中修改配置参数
*enableDynamicScriptOptimization*
。

## 参数

无。

## 返回值

无。

## 例子

```dolphindb
enableDynamicScriptOptimization()
```

**相关函数：**
[disableDynamicScriptOptimization](../d/disabledynamicscriptoptimization.html)
