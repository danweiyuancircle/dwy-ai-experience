# 10 条致命违规（零容忍）

> 何时引用：审查 DDB 代码 / SQL / Python SDK 用法。命中任意一条都属于零容忍违规，必须修复。
> 来源：dwy-dolphindb skill 内部规则（非官方文档可替代）。

| # | 违规 | 后果 |
|---|---|---|
| 1 | 分区列被函数包裹（`date(col)` / `year(col)` / `temporalAdd(col,...)`） | 全表扫 → OOM |
| 2 | 链式比较 `a <= col <= b` | 不触发剪枝 → 全表扫 |
| 3 | 单次 `append` > 500K 行 | TSDB 报 `exceeds max limit` |
| 4 | 未校验外部输入拼到脚本 | 脚本注入 |
| 5 | 连接池里 upload + run（变量跨连接不可见） | 变量找不到 |
| 6 | `select *`（30+ 列全传） | 浪费带宽和内存 |
| 7 | 分页用 `LIMIT x OFFSET y` | DDB 不支持 OFFSET 关键字（要用 `limit offset, count`） |
| 8 | `asyncio.to_thread(pool.run, script)` | SDK v3 `pool.run` 已是原生 async |
| 9 | SYMBOL 列写入未校验 ≤255 字节 | 整批写入失败 |
| 10 | 单分区 < 100MB 且总分区数 > 65536 | 触达 `maxPartitionNumPerQuery` 上限 |

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
