# DolphinDB 聚合 / 窗口 / 滑动函数速查

> 摘要文件，覆盖三大计算范式 + 滑动/累计/高阶组合 + 4 个典型案例 + 常见陷阱。完整列表见 `references/official/funcs/funcs_by_topics.md`。

## 一、三大计算范式对比

| 范式 | SQL 子句 / 高阶符号 | 输入 N 行 → 输出 | 典型场景 | 列表达式约束 |
|---|---|---|---|---|
| **分组聚合** | `group by` / `:G` | M 行（M = 组数） | 求每只股票的成交量总和 | 非分组列必须被聚合（sum/avg/...） |
| **保留行内分组** | `context by` / `:X` | N 行（行数不变） | 组内排名、组内累加、组内 z-score | 非分组列必须用「分组可分解函数」处理（聚合后广播 或 同长向量返回） |
| **窗口透视/对齐** | `pivot by` / `window join` / `window` | M×K 矩阵 / 对齐表 | 数据透视、按时间窗口对齐两表 | 行列各一个维度 |

口诀：
- `group by` → 压缩行（聚合）
- `context by` → 行数不变（分组内变换）
- `pivot by` → 行列转置（矩阵）

## 二、滑动函数（m\* 系列 / rolling / moving）

### 内置 m\* 系列（编译优化，性能最佳）

固定窗口大小，右边界对齐当前行。常见：

| 函数 | 含义 | 函数 | 含义 |
|---|---|---|---|
| `mavg(X, window)` | 滑动均值 | `mstd(X, window)` | 滑动标准差 |
| `msum(X, window)` | 滑动求和 | `mvar(X, window)` | 滑动方差 |
| `mmax/mmin(X, window)` | 滑动极值 | `mcorr(X, Y, w)` | 滑动相关系数 |
| `mcount(X, window)` | 滑动计数 | `mbeta(X, Y, w)` | 滑动 beta |
| `mmed(X, window)` | 滑动中位数 | `mrank(X, w)` | 滑动排名 |
| `mpercentile(X, p, w)` | 滑动分位数 | `mskew/mkurtosis` | 滑动偏度/峰度 |
| `mfirst/mlast` | 窗口首/末值 | `mimax/mimin` | 窗口极值位置 |

时间窗口版本：`tmavg / tmsum / tmstd / ...`，第三参传 duration（如 `3m`、`1h`）。

### 高阶 rolling / moving / window / tmoving / twindow

- `moving(func, X, window)`：对**任意聚合函数**滑动应用，窗口右对齐
- `rolling(func, X, window, step)`：跳跃式滑动（带 step）
- `window(func, X, leftOffset, rightOffset)`：左右边界**都可自由设定**（含未来数据）
- `tmoving / twindow`：时间窗口版本

性能：m\* 系列 > moving/rolling（高阶函数有调度开销）。能用 m\* 就不用 moving。

### TopN 变体（保留窗口内极值）

`msumTopN / mavgTopN / mcorrTopN / ...`：在窗口内取前 N 大值再计算。

## 三、累计函数（cum\* 系列）

从序列起点累积到当前位置。窗口大小 = 当前 index + 1。

| 函数 | 含义 |
|---|---|
| `cumsum / cumprod / cumavg / cummax / cummin` | 累积求和/积/均值/极值 |
| `cumstd / cumvar / cumcorr / cumbeta` | 累积统计量 |
| `cumcount / cumnunique` | 累积计数/累积去重数 |
| `cumrank / cumpercentile` | 累积排名/分位 |
| `cumfirstNot(X, v) / cumlastNot(X, v)` | 累积首个/末个非 v 值 |
| `cumPositiveStreak` | 累积正连续数 |

## 四、高阶函数模式速查

| 符号 | 名字 | 作用 | 等价 |
|---|---|---|---|
| `:E` | each | 对每个元素调用，结果组装 | `each(f, X)` |
| `:R / :L` | eachRight / eachLeft | 二元运算右/左固定 | `f:R(X, y)` 把 y 当标量 |
| `:P / :O` | eachPre / eachPost | 与前一/后一元素配对 | 相邻差分常用 `-:P` |
| `:A / :T` | accumulate / reduce | 类 fold 累积/归约 | `+:A` ≈ cumsum |
| `:G` | groupby | 函数式分组聚合 | `sum:G(X, key)` |
| `:X` | contextby | 分组内变换（行数不变） | 配合 SQL `context by` |
| `:C` | cross | 笛卡尔积应用 | 因子两两相关性 |
| `:H / :V` | byRow / byColumn | 矩阵按行/列应用 | 横截面统计 |
| —  | pivot | 行列转置 | 透视表 |
| —  | moving / window | 滑窗 / 自由窗 | 见上节 |
| —  | talib | 与 Python TA-Lib 行为一致 | TA-Lib 兼容层 |

带 `p` 前缀（pcross / peach / ploop）为并行版本。

## 五、典型用法 4 例

### 1. 合成 K 线（OHLC bar 聚合）

```dolphindb
// 按 1 分钟 bar 聚合 tick 为 K 线
select first(price) as open, max(price) as high,
       min(price) as low, last(price) as close,
       sum(volume) as vol
from tickTable
group by symbol, bar(timestamp, 60000) as minute
```

### 2. 组内排名（context by 保留行）

```dolphindb
// 每只股票每天的成交量在当天全市场的排名
select symbol, date, volume,
       rank(volume, false) + 1 as rk    // false = 降序
from t
context by date
```

### 3. 5 日移动均线（mavg）

```dolphindb
update t set ma5 = mavg(close, 5) context by symbol
// 等价（性能略差）：moving(avg, close, 5)
// 时间窗口版：tmavg(timestamp, close, 5m)
```

### 4. 截面 z-score（byRow + 横截面标准化）

```dolphindb
// 同一时刻横截面对所有股票因子做 z-score
select symbol, date,
       (factor - avg(factor)) \ std(factor) as zscore
from t
context by date
```

矩阵版用 `:H`：`zscore = (X - avg:H X) \ std:H X`。

## 六、常见陷阱

1. **`group by` 必须聚合非分组列**：`select symbol, price from t group by symbol` 报错 → 非分组列 `price` 必须用 `first/last/avg/sum` 等包裹。

2. **`context by` 列必须可分解**：
   - 合法：聚合后广播（`sum(x)`）、同长向量函数（`cumsum(x)` / `mavg(x, 5)` / `rank(x)`）
   - 非法：返回长度与组内行数不一致的函数（如不带广播规则的 reduce）

3. **m\* 函数 NULL 处理**：
   - 窗口内**任一**值为 NULL，结果默认 NULL
   - 跳过 NULL 用 `movingvalid(func, X, window)` 或 m\* 系列的 `minPeriod` 参数
   - 早期窗口（行号 < window）固定返回 NULL

4. **rolling 参数顺序**：`rolling(func, X, window, step)`，**step 默认 1**；与 moving 区别在 step（moving 始终 step=1）。

5. **time window 边界**：`tmavg(t, x, 5m)` 是**右闭**窗口（含当前 t）；要排除当前点用 `window` 自定义左右 offset。

6. **m\* 性能 > moving**：`mavg(x, 5)` 走 C++ 编译实现，`moving(avg, x, 5)` 是高阶调度，差距 10x+。

7. **`cum*` 与 `m*` 区别**：`cumsum` 窗口随 i 增长，`msum(x, w)` 窗口固定 w。

8. **`context by` + 排序**：分组内顺序敏感的函数（cumsum / mavg / rank）必须先 `order by` 保证组内行序。

## 下钻原文

- 函数分类总表：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/funcs_by_topics.md`
- 高阶函数总结：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/ho_funcs/ho_funcs.md`
- m\* 系列：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/m/` 下 mavg.md / msum.md / mstd.md / mcorr.md ...
- 累计：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/c/` 下 cum*.md
- 高阶细则：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/ho_funcs/` 下 contextby.md / moving.md / rolling.md / window.md / each.md / groupby.md / cross.md / byRow.md / byColumn.md / talib.md / tmoving.md / twindow.md
- SQL 子句：`/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/progr/sql/` 下 groupby.md / contextBy.md / cgroupby.md / pivotBy.md
