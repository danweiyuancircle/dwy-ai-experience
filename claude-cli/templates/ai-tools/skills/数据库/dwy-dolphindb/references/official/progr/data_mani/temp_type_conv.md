---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/temp_type_conv.html
fetched_at: 2026-05-19T09:02:19Z
category: progr
title: 时序类型和转换
sha1: d9878449a9b98a3cccfa950daec58aee3efe12ca
---

# 时序类型和转换

DolphinDB 支持以下九种时序数据类型：

| Data Type | Example |
| --- | --- |
| date | 2013.06.13 |
| month | 2012.06M |
| time | 13:30:10.008 |
| minute | 13:30m |
| second | 13:30:10 |
| datetime | 2012.06.13 13:30:10 or 2012.06.13T13:30:10 |
| timestamp | 2012.06.13 13:30:10.008 or 2012.06.13T13:30:10.008 |
| nanotime | 09:00:01.000100001 |
| nanotimestamp | 2016.12.30T09:00:01.000100001 |

我们可以使用时序类型转换函数把时序数据转换成另一种时序类型的数据。

```dolphindb
month(2016.02.14);
// output
2016.02M

date(2012.06.13 13:30:10);
// output
2012.06.13

second(2012.06.13 13:30:10);
// output
13:30:10

timestamp(2012.06.13 13:30:10);
// output
2012.06.13T13:30:10.000
```
