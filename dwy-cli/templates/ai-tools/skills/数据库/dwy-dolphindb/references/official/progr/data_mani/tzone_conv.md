---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/tzone_conv.html
fetched_at: 2026-05-19T09:02:21Z
category: progr
title: 时区和时区转换
sha1: f939b713fabd9aade2327556157c51df12a11cfa
---

# 时区和时区转换

DolphinDB中的时间序列对象不包括时区信息，它是由用户来决定时序对象的时区。

DolphinDB能够自动识别本地时区。我们可以使用以下函数实现时间转换：

(1) [localtime](../../funcs/l/localtime.html) 能够把零时区时间（格林尼治时间）转换成本地时间。

(2) [gmtime](../../funcs/g/gmtime.html) 能够把本地时间转换成零时区时间（格林尼治时间）。

(3) [convertTZ](../../funcs/c/convertTZ.html) 能够转换任意两个时区的时间。

如果原时区或目标时区实行夏令时，时区转换函数会自动处理夏令时。

## 例子

以下例子在美国东部时区执行：

```dolphindb
localtime(2018.01.22T15:20:26);
// output
2018.01.22T10:20:26

localtime(2017.12.16T18:30:10.001);
// output
2017.12.16T13:30:10.001

gmtime(2018.01.22 10:20:26);
// output
2018.01.22T15:20:26

gmtime(2017.12.16T13:30:10.008);
// output
2017.12.16T18:30:10.008

convertTZ(2016.04.25T08:25:45,"US/Eastern","Asia/Shanghai");
// output
2016.04.25T20:25:45

//美国实行夏令时
convertTZ(2016.04.25T19:25:45,"US/Eastern","Asia/Shanghai");
// output
2016.04.26T07:25:45
```
