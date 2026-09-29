# 10 条致命违规（零容忍）

> 何时引用：审查 DDB 代码 / SQL / Python SDK 用法。
> 分区剪枝、注入、连接池变量这些是语言约束，命中就要改。行数、字节、分区数是当时 server 的上限。官方文档或这次报错更准时，以那次为准，不要用本表压过当前版本文档。

| # | 违规 | 后果 |
|---|---|---|
| 1 | 分区列被函数包裹（`date(col)` / `year(col)` / `temporalAdd(col,...)`） | 全表扫 → OOM |
| 2 | 链式比较 `a <= col <= b` | 不触发剪枝 → 全表扫 |
| 3 | 单次 `append` 超过当前 server 的单消息上限（写作时常见约 500K 行） | TSDB 报 `exceeds max limit`。不是永远 500K |
| 4 | 未校验外部输入拼到脚本 | 脚本注入 |
| 5 | 连接池里 upload + run（变量跨连接不可见） | 变量找不到 |
| 6 | `select *`（30+ 列全传） | 浪费带宽和内存 |
| 7 | 分页用 `LIMIT x OFFSET y` | DDB 不支持 OFFSET 关键字（要用 `limit offset, count`） |
| 8 | `asyncio.to_thread(pool.run, script)` | SDK v3 `pool.run` 已是原生 async |
| 9 | SYMBOL 列写入未校验当前版本字节上限（1.30.23 / 2.00.11 起常见 255 字节） | 整批写入失败。以本次 server 文档为准 |
| 10 | 单分区过小且总分区数超过该节点 `maxPartitionNumPerQuery`（默认常见 65536） | 触达查询分区上限。配置改过就用配置值 |

## 审查输出格式

任务是**审查**他人代码时按此格式输出：

```
⚠️ [reference名] 具体问题
   违规代码：<摘录>
   修复建议：<可直接替换的代码>
   原因：<对应 reference 里的依据，一句话>

✅ [reference名] 符合要求 — <简要说明>
```

完整反模式细节见 [[anti-patterns]]。变更前自检见 [[change-checklist]]。
