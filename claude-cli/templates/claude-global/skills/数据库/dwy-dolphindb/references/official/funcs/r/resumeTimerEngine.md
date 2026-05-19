---
source_url: https://docs.dolphindb.cn/zh/funcs/r/resumeTimerEngine.html
fetched_at: 2026-05-19T09:36:24Z
category: funcs
title: resumeTimerEngine
sha1: a3d82f981602f059a8ae5cdff6bac4608bc397fd
---

# resumeTimerEngine

## 语法

`resumeTimerEngine(engine)`

## 详情

该函数只能通过 `useOrcaStreamEngine` 调用，恢复执行由
`DStream::timerEngine` 提交的任务。

## 参数

**engine** 表示引擎名称。字符串标量，可以传入完整的全限定名（如
"catalog\_name.orca\_engine.engine\_name"）；或引擎名（如 "engine\_name"），系统会根据当前的 catalog
设置自动补全为对应的全限定名。

## 例子

提交任务

```dolphindb
if (!existsCatalog("test")) {
	createCatalog("test")	
}
go
use catalog test

// 定义任务
def myFunc(x,y,z){
    writeLog(x,y,z)
}

// 定义参数
a = "aaa"
b = "bbb"
c = "ccc"

// 提交流图
g = createStreamGraph("timerEngineDemo")
g.source("trade", `id`price, [INT, DOUBLE])
 .timerEngine(3, myFunc, a, b, c)
 .setEngineName("myJob")
 .sink("result")
g.submit()
```

暂停任务执行

```dolphindb
useOrcaStreamEngine("myJob", stopTimerEngine)
```

继续执行任务

```dolphindb
useOrcaStreamEngine("myJob", resumeTimerEngine)
```

**相关函数：**[DStream::timerEngine](../d/DStream_timerEngine.html), [stopTimerEngine](../s/stopTimerEngine.html)
