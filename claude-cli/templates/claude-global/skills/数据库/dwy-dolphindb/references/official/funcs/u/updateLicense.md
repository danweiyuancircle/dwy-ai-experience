---
source_url: https://docs.dolphindb.cn/zh/funcs/u/updateLicense.html
fetched_at: 2026-05-19T09:43:18Z
category: funcs
title: updateLicense
sha1: 22f423ef3d4cabcfbe39966048fd50d84cd4db0b
---

# updateLicense

## 语法

`updateLicense()`

## 详情

用于在线更新 license。在手动替换 license 文件后执行该函数，可使新的 license
配置生效而无需重启节点。

更新配置生效规则如下：

- 立即生效：过期时间（expiration） 和 授权的节点个数（maxNodes） 的更新会立即生效。执行后，可通过 [getLicenseExpiration](../g/getLicenseExpiration.html) 获得当前
  license 的过期时间，以判断 license 是否生效。
- 需重启生效：若修改了除上述内容外的其它配置，如内存大小（maxMemoryPerNode）、CPU 核数（maxCoresPerNode）等，必须重启
  DolphinDB Server 才能使新配置生效。

注：

- 该函数仅在执行函数的节点生效。因此在集群环境下，需要在所有节点上运行该函数。
- 待升级 license 需满足以下条件才能成功升级（可通过
  `license` 函数查看）：

  - 授权的客户名称（cilentName）和授权模式（authorization）必须与原来的 license
    相同。
  - 授权的节点个数（maxNodes），内存大小（maxMemoryPerNode），CPU
    核数（maxCoresPerNode）不小于原 license 的授权。
- 若原 license 授权模式（authorization）为
  site，则无法进行在线升级。

## 参数

无

## 返回值

一个字典，表示许可证信息。

## 例子

```dolphindb
updateLicense()
// output
authorization->commercial
licenseType->0
maxMemoryPerNode->32
maxCoresPerNode->8
clientName->test license
bindCPU->true
expiration->2022.03.01
maxNodes->8
version->
modules->-1
```
