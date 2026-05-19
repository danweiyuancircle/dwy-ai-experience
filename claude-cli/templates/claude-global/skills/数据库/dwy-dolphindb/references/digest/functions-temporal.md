---
topic: functions-temporal
source_files:
  - official/funcs/funcs_by_topics.md
  - official/progr/data_mani/temp_obj_mani.md
  - official/progr/data_mani/tzone_conv.md
  - official/funcs/d/date.md
  - official/funcs/d/datetime.md
  - official/funcs/d/datehour.md
  - official/funcs/t/timestamp.md
  - official/funcs/n/now.md
  - official/funcs/t/today.md
  - official/funcs/t/temporalAdd.md
  - official/funcs/t/temporalDiff.md
  - official/funcs/t/temporalParse.md
  - official/funcs/t/temporalFormat.md
  - official/funcs/t/temporalSeq.md
  - official/funcs/b/businessDay.md
  - official/funcs/b/bar.md
  - official/funcs/a/addMarketHoliday.md
generated_at: 2026-05-19
---

# 时间日期函数

## 何时用此主题
用户问"DolphinDB 有哪些日期/时间函数"、"DATETIME 和 TIMESTAMP 区别"、"如何取上一个交易日"、"如何按 5 分钟做 K 线分桶"、"如何把字符串解析成时间"、"时区怎么转"、"如何加减月/年"。

## 时间类型选择
DolphinDB 时序对象**不包含时区信息**,时区由应用层决定(详见下方时区转换)。

| 类型 | 精度 | 字面量示例 | 范围 | 注意 |
|---|---|---|---|---|
| `DATE` | 日 | `2024.01.05` | 较大 | 仅日期 |
| `MONTH` | 月 | `2024.01M` | 较大 | 仅年月 |
| `TIME` | 毫秒 | `13:30:10.008` | 0..86399999 | 仅一日内时间 |
| `MINUTE` | 分 | `13:30m` | 0..1439 | 仅一日内分钟 |
| `SECOND` | 秒 | `13:30:10` | 0..86399 | 仅一日内秒 |
| `NANOTIME` | 纳秒 | `13:30:10.008007006` | 0..86400000000000-1 | 仅一日内纳秒 |
| `DATETIME` | 秒 | `2024.01.05 13:30:10` | **[1901.12.13T20:45:53, 2038.01.19T03:14:07]** | **2038 溢出风险,生产慎用** |
| `TIMESTAMP` | 毫秒 | `2024.01.05 13:30:10.008` | 64 位 | **推荐**(常用毫秒级精度) |
| `DATEHOUR` | 小时 | `2024.01.05T13` | 较大 | 小时桶分区列常用 |
| `NANOTIMESTAMP` | 纳秒 | `2024.01.05 13:30:10.008007006` | 64 位 | 高频/Tick 行情 |

## 构造与转换
| 函数 | 用途 | 例子 |
|---|---|---|
| `date(X)` | 转 DATE | `date(now()) → 2024.02.22` |
| `datetime(X)` | 转 DATETIME(秒) | `datetime(2009.11.10) → 2009.11.10 00:00:00` |
| `timestamp(X)` | 转 TIMESTAMP(毫秒) | `timestamp(2016.10.12) → 2016.10.12 00:00:00.000` |
| `datehour(X)` | 转 DATEHOUR(小时) | `datehour(2012.06.13 13:30:10) → 2012.06.13T13` |
| `nanotimestamp(X)` | 转纳秒时间戳 | 高频场景 |
| `month/minute/second/time/nanotime` | 各自类型构造器 | — |
| `concatDateTime(d, t)` | 合并日期+时间 | `concatDateTime(2019.06.15,13:25:10) → 2019.06.15T13:25:10` |
| `temporalParse(s, format)` | 字符串 → 时间(别名 `datetimeParse`) | `temporalParse("14-02-2018","dd-MM-yyyy") → 2018.02.14` |
| `temporalFormat(t, format)` | 时间 → 字符串(别名 `datetimeFormat`) | `temporalFormat(2018.02.14,"dd-MMM-yy") → "14-FEB-18"` |
| `now([nanoSecond=false])` | 当前 TIMESTAMP/NANOTIMESTAMP | — |
| `today()` | 当前 DATE | — |

`format` 元素:`yyyy/yy/MM/MMM/dd/HH/hh/mm/ss/aa/SSS/nnnnnn/nnnnnnnnn`,其他字符均为分隔符。

## 提取部分
全部按字面名理解,均接受标量或向量:

- 年月日:`year` / `month`(返回 MONTH 类型) / `monthOfYear`(返回 1-12 整数) / `dayOfMonth` / `dayOfYear` / `daysInMonth`
- 周:`weekday` / `dayOfWeek` / `weekOfYear` / `weekOfMonth`
- 季:`quarterOfYear`
- 时分秒:`hour` / `hourOfDay` / `minuteOfHour` / `secondOfMinute` / `millisecond` / `microsecond` / `nanosecond`
- 闰年判断:`isLeapYear`

## 时间运算
- 直接 `+ / -` 整数:按对应类型的最小单位增减(`DATE` 加天、`MINUTE` 加分、`TIMESTAMP` 加毫秒)。`MINUTE/TIME/SECOND/NANOTIME` 一日内类型会取模,如 `23:59m + 10 → 00:09m`。
- `temporalAdd(obj, duration, unit)`(别名 `datetimeAdd`):按 `ns/us/ms/s/m/H/d/w/M/y/B`(工作日) 或**交易日历标识**(如 `XNYS`)增减。
- `temporalDiff(X, Y, [unit])`(3.00.3+,别名 `datetimeDiff`):时间差,`unit` 取 `d`/`B`/交易日历标识时 X、Y 必须是 DATE。
- `temporalDeltas(X, [step=1])`:相邻元素时间差。
- `temporalSeq(start, end, rule, ...)`:按 `rule`(`B/W/M/MS/Q/D/H/min/S/...`) 重采样生成时间序列。
- `bar(X, interval, [closed='left'])`:**核心分桶函数**,K 线/时间窗口必备。`interval` 支持 DURATION(`5m`、`1H`、`30s`),不支持 `y`/`M`(年/月用 `year(x)` / `month(x)` 转换后用整数分组)。

## 周期边界(对齐 pandas DateOffset)
- 年:`yearBegin` / `yearEnd` / `businessYearBegin` / `businessYearEnd` / `isYearStart` / `isYearEnd`
- 月:`monthBegin` / `monthEnd` / `businessMonthBegin` / `businessMonthEnd` / `semiMonthBegin` / `semiMonthEnd` / `isMonthStart` / `isMonthEnd`
- 季:`quarterBegin` / `quarterEnd` / `businessQuarterBegin` / `businessQuarterEnd` / `isQuarterStart` / `isQuarterEnd`
- 周:`weekBegin` / `weekEnd` / `weekOfMonth` / `lastWeekOfMonth`
- 半年:`semiannualBegin` / `semiannualEnd`
- 财年(52/53 周制):`fy5253` / `fy5253Quarter`
- 区间:`duration("5M")` / `duration("3XNYS")`(支持交易日历)

## 交易日历(金融场景)
默认 `businessDay` 把周六日视作非工作日。要按真实交易所节假日,需先注册交易日历:

| 函数 | 用途 |
|---|---|
| `addMarketHoliday(marketName, holiday, [dateType])` | 注册交易日历(管理员;`marketName` 必须 4 个大写字母,如 `XNYS`、`XSHG`) |
| `updateMarketHoliday` / `deleteMarketHoliday` | 维护交易日历 |
| `getMarketCalendar(marketName)` | 查询某市场交易日历 |
| `listAllMarkets()` | 列出已注册市场 |
| `getinstrumentcalendar` / `gettradingcalendartype` | 合约/类型查询 |
| `businessDay(X, [offset], [n=1])` | 最近工作日 |
| `temporalAdd(d, 5, "XNYS")` | 按交易日加减 |
| `temporalDiff(d1, d2, "XNYS")` | 按交易日算差 |

注册后,`temporalAdd` / `temporalDiff` / `duration` 的 `unit` 都可直接传 `marketName`(如 `"XNYS"`)。

## 时区转换
DolphinDB 时序对象**无时区**(裸时间戳),要换时区显式调用:

- `localtime(t)`:GMT → 本地时区
- `gmtime(t)`:本地 → GMT
- `convertTZ(t, fromTZ, toTZ)`:任意时区互转,自动处理夏令时

```dolphindb
convertTZ(2016.04.25T08:25:45, "US/Eastern", "Asia/Shanghai")
// → 2016.04.25T20:25:45
```

## 典型用法
```dolphindb
// 1. 合成 5 分钟 K 线(高频 Tick → 分钟桶)
select first(price) as open, max(price) as high, min(price) as low,
       last(price) as close, sum(volume) as vol
from tick
group by symbol, bar(ts, 5m) as bucket  // ts: TIMESTAMP

// 2. 上一个 XNYS 交易日
prevTrade = temporalAdd(today(), -1, "XNYS")

// 3. 字符串日志 → TIMESTAMP
ts = temporalParse("2024-03-15 09:30:00.123", "yyyy-MM-dd HH:mm:ss.SSS")

// 4. 取本月最后一个工作日
businessMonthEnd(today())

// 5. 按日历自然日数算账龄
ageDays = temporalDiff(today(), openDate, "d")
```

## 常见陷阱
- **DATETIME 慎用**:范围仅到 2038.01.19,生产数据统一用 `TIMESTAMP`(毫秒) 或 `NANOTIMESTAMP`(纳秒)。
- **分区列上调用函数破坏分区剪枝**:`where year(ts)=2024` 会全表扫,改为 `where ts >= 2024.01.01 and ts < 2025.01.01`(详见 [[partitioning]])。
- **时区不在类型里**:跨时区存储/展示必须应用层 `convertTZ`,否则同一个 `TIMESTAMP` 在不同节点解读不同。
- **`bar` 不支持年/月**:`bar(ts, 1M)` 报错,改 `group by year(ts)*100 + monthOfYear(ts)` 或 `group by month(ts)`。
- **`MINUTE/TIME/SECOND/NANOTIME` 加减会取模**:跨天加减后看似"回到当天",不要用一日内类型做跨天运算,统一用 `TIMESTAMP`。
- **`businessDay` 默认只跳周末**:真实节假日需先 `addMarketHoliday` 注册交易日历,再用 `temporalAdd(d, n, "XNYS")`。
- **`temporalParse` 分隔符必须严格匹配**:`"14-02-2018"` 配 `"dd/MM/yyyy"` 解析失败返回 `00d`(NULL)。
- **`now()` 在 Windows 上可能无纳秒精度**,即便传 `nanoSecond=true`。

## 下钻原文
- `official/funcs/funcs_by_topics.md` — 官方"时间处理"全清单
- `official/progr/data_mani/temp_obj_mani.md` — 时序对象运算/边界对齐总览
- `official/progr/data_mani/tzone_conv.md` — 时区与 DST
- `official/funcs/t/temporalAdd.md` / `temporalDiff.md` / `temporalParse.md` / `temporalFormat.md` / `temporalSeq.md`
- `official/funcs/b/bar.md` — 分桶(K 线)
- `official/funcs/b/businessDay.md` / `official/funcs/a/addMarketHoliday.md` — 交易日历
- `official/funcs/c/convertTZ.md` / `official/funcs/l/localtime.md` / `official/funcs/g/gmtime.md` — 时区
