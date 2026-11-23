---
source_url: https://docs.dolphindb.cn/zh/funcs/d/DStream_timerEngine.html
fetched_at: 2026-05-19T09:20:22Z
category: funcs
title: DStream::timerEngine
sha1: 29821c749fdcc60fd3dcb33c5865c1cf3ccadde6
---

# DStream::timerEngine

## 语法

`DStream::timerEngine(interval, func, args...)`

## 详情

定义一个时间触发引擎，以间隔 *interval* 周期性地执行 *func*。执行该任务不会阻塞或修改流图的数据流。

## 参数

**interval** 整型标量，表示任务执行的时间间隔，单位为秒。

**func** FUNCTIONDEF 标量，表示定时执行的任务。

**args…** 传递给 *func* 的参数，使用方式类似于远程过程调用函数 [rpc](../r/rpc.html) 的 *args…* 参数。当 *func* 为无参函数时可省略。

## 返回值

返回一个 DStream 对象。

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

**相关函数：**[resumeTimerEngine](../r/resumeTimerEngine.html), [stopTimerEngine](../s/stopTimerEngine.html)
