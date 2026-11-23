---
topic: sql-essentials
source_files: [official/progr/sql/sql_intro.md, official/progr/sql/Select.md, official/progr/sql/exec.md, official/progr/sql/where.md, official/progr/sql/groupby.md, official/progr/sql/contextBy.md, official/progr/sql/pivotBy.md, official/progr/sql/cgroupby.md, official/progr/sql/having.md, official/progr/sql/orderby.md, official/progr/sql/limit.md, official/progr/sql/top.md, official/progr/sql/join.md, official/progr/sql/equijoin.md, official/progr/sql/leftjoin.md, official/progr/sql/asofjoin.md, official/progr/sql/windowjoin.md, official/progr/sql/interval.md, official/progr/sql/in.md, official/progr/sql/between.md, official/progr/sql/predicates.md, official/progr/sql/exe_order.md]
generated_at: 2026-05-19
---

# DolphinDB SQL 核心要点

## 何时用此主题

写 SELECT/JOIN/GROUP BY/分页/排序等基础查询时进来；确认 DolphinDB SQL 与 MySQL/PostgreSQL 写法差异时；写 K 线合成、TopN、时序对齐等金融典型查询时。

## DolphinDB SQL 与标准 SQL 的关键差异

| 特性 | 标准 SQL | DolphinDB |
|---|---|---|
| 分页 | `LIMIT count OFFSET m` | `limit offset, count`（顺序反过来） |
| 取标量/向量 | `SELECT` 一律返回结果集 | `select` 必返回 table，要标量/向量用 `exec` |
| 分组保留全部行 | window `OVER` | `context by`（每组返回与组内行数等长的向量） |
| 透视 | 子查询拼装 | `pivot by`（与 select → 表，与 exec → 矩阵） |
| 累计分组 | window `ROWS UNBOUNDED PRECEDING` | `cgroup by`，必须配 `order by` |
| 时间最近匹配 | 无 | `aj`（asof join） |
| 窗口聚合 join | 无 | `wj` / `pwj` |
| 等距时间分组+插值 | `DATE_TRUNC` + group by | `group by interval(time, 5m, "prev")` |
| top 写法 | `LIMIT n` | `top n` 或 `top start:end`（左闭右开，只能整型常量） |
| where `=` / `==` | 仅赋值/比较 | where 中 `==` 等价 `=` |
| 非等值 join | 支持 | **不支持**（`t1.x > t2.x` 不能写 ON） |

## select / exec 区别

- `select` 永远返回 table（哪怕 1×1）
- `exec` 单列 → vector；单行单列聚合 → scalar；多列 → table；配 `pivot by` → matrix
- 查询结果要参与后续标量运算必须 `exec`

## where 子句最佳实践

- `and` / `&&` / `,` 都是与，但 `,` 是**逐条过滤**（先过滤最左，再在结果上过滤下一条），`and` 是**各自过滤再取交集**
- `or` / `||` 是或
- `between v1 and v2` ≡ `between v1:v2`（闭区间）
- `in (v1, v2)` / `in (subquery)` 替代多 or 和子查询
- 标量子查询：`where col > (select avg(col) from t)`（单行单列 select 自动当标量）
- 谓词清单：`not` / `is null` / `is not null` / `between and` / `exists` / `in` / `like` / `notLike` / `notBetween` / `notIn`
- **不能用 select 里 `as` 起的别名**（where 在 select 之前执行），having / order by 才可以

## group by / context by / pivot by / cgroup by 选择

| 场景 | 用什么 |
|---|---|
| 分组聚合，每组一行 | `group by` |
| 分组保留每行（组内累计/ratio/拟合） | `context by` |
| 透视成二维表（行 × 列） | `pivot by` |
| 累计分组（含前面所有组） | `cgroup by` + `order by` |
| 等距时间窗口分组（含插值） | `group by interval(time, 5m, "prev")` |

`context by` 关键点：必配顺序敏感函数（`cumsum` / `mavg` / `ratios` / `deltas` / `first` / `last`）；用 `csort col [asc|desc]` 在组内排序；配 `limit n` / `limit -n` 取每组前/后 n 条；`csort time desc limit 2` = 每组时间最近 2 条。

## window 函数（窗口聚合）

DolphinDB **不用** SQL 标准 `OVER` 语法，改用：
- `context by` + 滑动函数（`mavg` / `mcount` / `msum` / `mmax`）
- `wj` / `pwj` 把窗口聚合做成 join
- 数组向量列用 `rowSum` / `rowMax` 等行级函数

## join 类型

| SQL 关键字 | 函数 | 含义 |
|---|---|---|
| `inner join` | `ej` / `sej`（结果排序版） | 等值连接 |
| `left [outer] join` | `lj` | 右表多行匹配全保留 |
| `left semijoin` | `lsj` | 右表多行匹配只取首条（行数 = 左表） |
| `full join` | `fj` | 全外 |
| `cross join` | `cj` | 笛卡尔积；无 `ON` 的 join 也是 cross |
| `aj(...)` | asof | 时间最近匹配，右表取 ≤ t 最后一条 |
| `wj/pwj(...)` | window | 对左表每行取右表 `[t+w1, t+w2]` 应用聚合函数 |

约束：多连接列必须用 `and`（不支持 or）；自连接必须用别名；连接分布式表时分组列必须包含全部分区字段。

## 典型查询模板

K 线合成（5 分钟 OHLCV）：
```dolphindb
select first(price) as open, max(price) as high, min(price) as low,
       last(price) as close, sum(volume) as vol
from trades
group by sym, interval(time, 5m, "none")
```

每只股票 TopN（按成交量取前 3）：
```dolphindb
select top 3 * from trades context by sym csort volume desc
```

trade 对 quote 时序对齐：
```dolphindb
select * from aj(trades, quotes, `sym`time)
```

组内累计与收益率：
```dolphindb
select sym, time, price, cumsum(volume) as cumVol, ratios(price)-1 as ret
from t context by sym csort time
```

每组最新 1 条（行情快照）：
```dolphindb
select * from t context by sym csort time desc limit 1
```

行情转矩阵：
```dolphindb
priceMatrix = exec price from t pivot by time, sym
```

## 常见陷阱

- `select count(*) from t` 返回 1×1 table；要数字用 `exec count(*) from t`
- 分页是 `limit offset, count`，不是 `LIMIT count OFFSET offset`
- `top n`、`top a:b` 只能用整型**常量**，禁止变量/表达式
- `top` 不能与 `pivot by` 共用；`context by` + `top` 不允许 `top a:b` 范围
- `csort` 只在配合**序列函数/聚合函数/having/limit** 时真正排序
- `where` 不能用 select 别名
- `,` 与 `and` 在边缘场景过滤路径不同
- `group by` 列**自动加入结果**且排在最前，无需 select 中写
- `pivot by` 行列重复时默认保最后一条；保全量需 `asis(col)` 且满足 DFS+分区列等多条限制
- 暂**不支持非等值 join**

## 执行顺序

`from / on` → `where` → `group by` / `context by` / `pivot by` → `csort` → `having` → `select` → `distinct` → （有 `context by`）`limit` → `order by` → （无 `context by`）`limit`

要点：where 在 select 之前 → where 不能用别名；order by 在 select 之后 → 可用别名；有 `context by` 时 limit 作用于每组且在 order by 之前，否则作用于全表且在 order by 之后。

## 下钻原文

- `official/progr/sql/sql_intro.md` — 语法总览与 SQL-92 差异对照
- `official/progr/sql/exe_order.md` — 子句执行顺序与示例
- `official/progr/sql/Select.md` / `exec.md` — select vs exec 返回形态
- `official/progr/sql/contextBy.md` / `groupby.md` / `pivotBy.md` / `cgroupby.md` — 四种分组语义
- `official/progr/sql/asofjoin.md` / `windowjoin.md` / `equijoin.md` / `leftjoin.md` / `join.md` — 各类 join
- `official/progr/sql/interval.md` — 等距时间分组与插值
- `official/progr/sql/predicates.md` / `in.md` / `between.md` — where 谓词
- `official/progr/sql/top.md` / `limit.md` / `orderby.md` / `having.md` — 分页排序过滤
