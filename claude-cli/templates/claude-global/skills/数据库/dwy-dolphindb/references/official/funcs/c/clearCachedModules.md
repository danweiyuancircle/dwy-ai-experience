---
source_url: https://docs.dolphindb.cn/zh/funcs/c/clearCachedModules.html
fetched_at: 2026-05-19T09:15:16Z
category: funcs
title: clearCachedModules
sha1: 296e904f24c5fee1ceb44e00113d3c81cdc9ca9f
---

# clearCachedModules

## 语法

`clearCachedModules()`

## 详情

清除缓存的 module。更新 module 文件后，通过该命令清除 module 缓存，执行 use 语句时，会重新从文件加载 module，无需重启节点。

注：

只有管理员（admin）才能执行该命令。

## 参数

无

## 返回值

无。

## 例子

定义并导入一个 module

```dolphindb
module printLog
def printLog(){
print "hello"
}
```

加载模块

```dolphindb
use printLog
printLog()
// output
hello
```

修改 module

```dolphindb
module printLog
def printLog(){
print "hello new"
}
```

再次加载模块前，需要调用 `clearCachedModules` 以清除之前缓存的
module。

```dolphindb
login("admin", "123456")

clearCachedModules();

use printLog
printLog()
// output
hello new
```
