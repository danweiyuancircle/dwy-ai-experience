---
name: dwy-dolphindb
description: "DolphinDB 3.0 社区版（2核8G / 1控2节点）开发与审查 skill：写 DolphinDB Script (.dos)、用 Python SDK (dolphindb 3.0.4)、设计 DFS 分区表（TSDB/OLAP/PKEY/IMOLTP/VECTORDB 引擎选型）、导入 tick/snapshot/kline 金融数据、优化慢查询、排查 OOM / 卡死作业、Docker 部署、查询日期/字符串/聚合等内置函数、流计算、回测、集群运维。可基于项目级 .claude/dolphindb/schemas/ 真实 DDL 做查询性能评估。也用于代码审查：检查分区裁剪、链式比较、批量写入上限、SYMBOL 字节限制、STRING/BLOB 静默截断、输入校验防脚本注入、连接池配置、pool.run async/sync 用法。关键字触发：dolphindb, DDB, .dos, loadTable, loadTextEx, createPartitionedTable, append!, dropPartition, DBConnectionPool, tableAppender, PartitionedTableAppender, MultithreadedTableWriter, TSDB, OLAP, PKEY, IMOLTP, VECTORDB, getClusterPerf, getConsoleJobs, level2, tick 数据, 时序数据库, 8848 端口, 交易日历, 函数参考, K线合成, 流引擎, 回测引擎."
source_url_base: https://docs.dolphindb.cn/zh
fetched_at: 2026-05-19
---

# DolphinDB 3.0 Skill

## 当前环境

| 项 | 值 |
|---|---|
| 版本 | DolphinDB 3.0 社区版 |
| 拓扑 | 1 控制节点 + 2 计算/数据节点 |
| 资源 | 2 核 / 8GB 内存（已分配 3GB），磁盘 33 TB |
| 端口 | Web/控制 `http://localhost:8848`，集群另含 `192.168.0.107:8848` / `172.17.0.1:8848` 等 |
| Worker | 4 线程，连接上限 512（当前 15） |
| Python SDK | `dolphindb==3.0.4` |
| 场景 | 个人/小团队 + 教学，**单查询内存上限按 2GB 控制** |

## 文档分层（按访问顺序）

1. **`references/digest/`** —— 🎯 **第一站**，12 份金融/高频主题核心摘要（每份 100-180 行）。90% 问题在这里命中
2. **`references/review-rules/`** —— skill 自带审查规则（致命违规、反模式、基线、变更检查清单），代码审查时必读
3. **`references/INDEX.md`** —— 文档主索引（自动生成，digest + review-rules + 官方文档全目录）
4. **`references/official/`** —— 官方中文文档全量（`docs.dolphindb.cn/zh/`），**下钻用**
5. **`references/official/funcs/_INDEX.md`** —— 1705 个函数按字母分组的二级索引

**路由顺序**：digest → review-rules → official。先看 digest，命中就够；不够再下钻 official 对应章节。

## 何时进入哪份 reference（路由表）

### 优先看 digest（100-180 行精华，覆盖 90% 问题）

| 问题类型 | digest 文件 | 下钻 official |
|---|---|---|
| 引擎选型（TSDB/OLAP/PKEY/IMOLTP/VECTORDB） | `digest/engines.md` | `official/db_distr_comp/db/` |
| 分区策略 / sortColumns / 分区剪枝 | `digest/partitioning.md` | `official/db_distr_comp/db/` |
| DDB SQL 写法 / select/where/group/context/pivot/join | `digest/sql-essentials.md` | `official/progr/sql/` |
| 时间日期函数 / 交易日历 / 时间类型选型 | `digest/functions-temporal.md` | `official/funcs/d/`, `t/`, `m/` |
| 聚合 / 窗口 / 滑动 / 累计函数 | `digest/functions-aggregate-window.md` | `official/funcs/m/`, `r/`, `c/contextby.md` |
| 字符串函数 / SYMBOL / 编码 | `digest/functions-string.md` | `official/funcs/s/`, `r/regex*` |
| Python SDK 连接/写入/订阅/异步 | `digest/python-sdk.md` | `official/pydoc/` |
| 数据导入 / loadTextEx / 批量写 | `digest/data-ingest.md` | `official/db_distr_comp/db_oper/` |
| 流引擎 / CEP / 实时计算 | `digest/stream-engine.md` | `official/stream/` |
| 性能调优 / OOM / 慢查询定位 | `digest/perf-tuning.md` + `review-rules/perf-baselines.md` | `official/sys_man/` |
| 部署 / HA / 备份恢复 / 监控 | `digest/deploy-ops.md` | `official/deploy/`, `official/sys_man/` |
| 金融场景（K 线 / 因子 / TopN / 回测） | `digest/finance-patterns.md` | `official/tutorials/`, `official/backtest/` |

### digest 未覆盖时直查 official

| 问题类型 | 路径 |
|---|---|
| 查特定函数（已知函数名） | `official/funcs/_INDEX.md` → `official/funcs/{letter}/{name}.md` |
| 按主题找函数（官方分类） | `official/funcs/funcs_by_topics.md` |
| 其他语言 API（C++/Java/Go/JS/C#/R） | `official/api/` |
| 错误码 / 报错排查 | `official/error_codes/` |
| 插件（DataX / Kafka / Grafana 等） | `official/plugins/` |
| 编程语言（DDB 脚本语法） | `official/progr/` |
| 版本说明 / Release Notes | `official/rn/`, `official/pydoc/release_notes/` |

### 代码审查 / 性能评估

| 问题类型 | 路径 |
|---|---|
| 代码审查 / 查反模式 / 找致命违规 | `review-rules/lethal-violations.md` + `review-rules/anti-patterns.md` |
| 写前自检清单 | `review-rules/change-checklist.md` |
| 评估查询性能 + 真实 schema | `review-rules/perf-baselines.md` + `digest/perf-tuning.md` + 项目级 schema（见下） |
| 真实环境 SQL/DDL 接入 | `references/project-schema-protocol.md` |

## 评估查询性能时（项目级 schema 协议）

用户问"这个 SQL 为何慢"、"评估这个建表"、"分析查询内存" 等问题时：

1. **先 `ls {项目根}/.claude/dolphindb/schemas/`**，看是否有相关表的 DDL
2. **有** → 读出来基于真实分区策略 / sortColumns / 数据类型给评估
3. **无** → 主动提示用户按 [[project-schema-protocol]] 协议把 DDL 粘到对应路径

不要在没有 DDL 的情况下凭空猜测分区策略给建议。

## 30 秒速查

```dolphindb
// 连接（Python）
import dolphindb as ddb
s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")

// 看集群健康
s.run("getClusterPerf()")                       // CPU/内存/磁盘
s.run("getRecentJobs(20)")                      // 最近 20 个批作业
s.run("pnodeRun(getConsoleJobs)")               // 所有节点同步作业
s.run("getSessionMemoryStat()")                 // 当前 session 内存

// 看库表
s.run("getClusterDFSDatabases()")               // 所有 DFS 库
s.run("getClusterDFSTables('dfs://xxx')")       // 库下所有表
s.run("schema(loadTable('dfs://xxx','t'))")     // 表结构

// 杀作业（按 rootJobId）
s.run("cancelJob(`xxxx)")                       // 异步作业
s.run("cancelConsoleJob(`xxxx)")                // 同步作业
```

## 核心原则（社区版 2 核 8G 死守）

1. **单查询不超 2GB**：详见 [[review-rules/perf-baselines]]
2. **任何 WHERE 必带分区列**且不被函数包裹 / 不写链式比较
3. **TSDB sortColumns 不要选唯一/高基数列**（索引膨胀）
4. **写入用 PartitionedTableAppender + DBConnectionPool**（pool size 3）
5. **删数据按分区 `dropPartition`**，不用 `delete from`

完整规则 → [[review-rules/lethal-violations]] + [[review-rules/anti-patterns]]

## 审查模式

代码 review / CR 任务按此格式输出：

```
⚠️ [reference 名] 具体问题
   违规代码：<摘录>
   修复建议：<可直接替换的代码>
   原因：<对应 reference 里的依据，一句话>

✅ [reference 名] 符合要求 — <简要说明>
```

审查依据按优先级：
1. `review-rules/lethal-violations.md` —— 10 条零容忍违规
2. `review-rules/anti-patterns.md` —— 类型/SQL/库表/写入/运维反模式
3. `review-rules/change-checklist.md` —— 17 项变更前自检
4. `official/` —— 官方文档的具体规则

## skill 维护命令

文档来自爬取，需要周期刷新。所有命令在 skill 目录下跑：

```bash
cd .     # skill 根目录

# 检查文档新鲜度（默认 90 天阈值）
uv run scripts/check_freshness.py
uv run scripts/check_freshness.py --days 30

# 增量更新（sha1 未变则跳过）
uv run scripts/refresh_docs.py --all                  # 全量增量
uv run scripts/refresh_docs.py --section funcs        # 仅 funcs 章节
uv run scripts/refresh_docs.py --section pydoc        # 仅 Python SDK

# 强制重爬（忽略 manifest）
uv run scripts/refresh_docs.py --rebuild --all

# 重新生成索引（爬完自动生成，但手改 frontmatter 后需重跑）
uv run scripts/build_index.py
```

## 官方文档基础链接

完整索引见 [[INDEX]]。常用入口：
- 主站：https://docs.dolphindb.cn/zh/about/ddb_intro.html
- 函数参考：https://docs.dolphindb.cn/zh/funcs/funcs_intro.html
- Python SDK：https://docs.dolphindb.cn/zh/pydoc/py.html
- 金融入门教程：https://docs.dolphindb.cn/zh/tutorials/new_users_finance.html
- 使用须知：https://docs.dolphindb.cn/zh/tutorials/usage_guidelines.html
