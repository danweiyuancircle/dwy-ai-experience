---
source_url: https://docs.dolphindb.cn/zh/funcs/g/generateMachineFingerprint.html
fetched_at: 2026-05-19T09:22:25Z
category: funcs
title: generateMachineFingerprint
sha1: dfdb8a0c5dda6f131f71b061a95349ef71ba7b93
---

# generateMachineFingerprint

## 语法

`generateMachineFingerprint(outputPath)`

## 参数

**outputPath** 是字符串，表示存放机器指纹的目录。

## 详情

生成机器指纹，用于 license 验证。该命令必须要用户登录后才能执行。Windows 操作系统下执行该函数需要管理员权限。

## 例子

```dolphindb
generateMachineFingerprint("/home/DolphinDB")
```
