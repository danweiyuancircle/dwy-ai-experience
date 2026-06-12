---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setDefaultCatalog.html
fetched_at: 2026-05-19T09:38:33Z
category: funcs
title: setDefaultCatalog
sha1: d2639be93238657b864e27f814d3474d32a9a444
---

# setDefaultCatalog

## 语法

`setDefaultCatalog(catalog)`

## 详情

为当前 session 设置默认的 catalog。

## 参数

**catalog** 字符串标量，表示 catalog 的名称。若为空，则表示重置当前 catalog 空间为初始状态，即无默认 catalog。

## 例子

```dolphindb
getCurrentCatalog()
// 返回为空

createCatalog("cat1")
setDefaultCatalog("cat1")
getCurrentCatalog()
// Output: cat1

setDefaultCatalog("")
getCurrentCatalog()
// 返回为空
```
