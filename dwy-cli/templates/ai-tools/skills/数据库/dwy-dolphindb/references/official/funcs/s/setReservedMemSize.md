---
source_url: https://docs.dolphindb.cn/zh/funcs/s/setReservedMemSize.html
fetched_at: 2026-05-19T09:39:00Z
category: funcs
title: setReservedMemSize
sha1: 03e2c322d50f7867274bd09038882e3778550811
---

# setReservedMemSize

## 语法

`setReservedMemSize(memSizeGB)`

## 详情

在线修改系统预留内存空间的大小。该命令只能由管理员执行。

请注意：

- 此命令修改的配置值在系统重启后将失效。若需要配置值永久生效，请更改配置文件中的 *reservedMemSize*。
- 此函数所设置的预留内存空间大小（对应配置项 *reservedMemSize*）与紧急内存区空间大小（对应配置项 *emergencyMemSize*
  或通过`setMaxMemSize`在线修改），其值相加不可超过当前最大内存空间（对应配置项 *maxMemSize*
  或通过`setMaxMemSize`在线修改）的 50%。

## 参数

**memSizeGB** 一个数值型标量（单位为GB），必须大于0，且不能超过 *maxMemSize* \* 0.5。
