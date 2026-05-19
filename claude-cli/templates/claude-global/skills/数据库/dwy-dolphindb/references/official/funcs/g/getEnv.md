---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getEnv.html
fetched_at: 2026-05-19T09:23:42Z
category: funcs
title: getEnv
sha1: 3689018d6a2f7cddedf36d6ddaa7eaeaf7f7dc40
---

# getEnv

## 语法

`getEnv(name, [default])`

## 详情

查询指定环境变量的值。如果环境变量不存在，则返回 default 参数。

## 参数

**name** 是字符串标量，表示环境变量名称。

**default** 是字符串标量，表示不存在对应的环境变量时返回的默认值。如果没有指定 default，默认值为空字符串。

## 返回值

字符串标量。

## 例子

```dolphindb
getEnv("path")
```

返回：C:\ProgramData\DockerDesktop\version-bin;C:\Program
Files\Docker\Docker\Resources\bin;

```dolphindb
getEnv("JAVA_HOME");
```

返回：C:\Program Files\Java\jdk1.8.0\_191

```dolphindb
getEnv("not_exist","not exist")
```

返回：`not exist`
