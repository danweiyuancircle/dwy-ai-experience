---
source_url: https://docs.dolphindb.cn/zh/funcs/d/disabledynamicscriptoptimization.html
fetched_at: 2026-05-19T09:19:01Z
category: funcs
title: disableDynamicScriptOptimization
sha1: 14aa4afe9bc511eabcdfb35860e8565721769be0
---

# disableDynamicScriptOptimization

## 语法

`disableDynamicScriptOptimization()`

## 详情

关闭脚本引擎优化。

此命令须在控制节点由管理员执行。

此命令的影响将在系统重启后失效。若要永久生效，请在配置文件（集群模式为 controller.cfg，单节点模式为 dolphindb.cfg）中修改配置参数
*enableDynamicScriptOptimization*
。

## 例子

```dolphindb
disableDynamicScriptOptimization()
```

**相关函数：**
[enableDynamicScriptOptimization](../e/enabledynamicscriptoptimization.html)
