# dwy_log 测试范围

2026-11-16：Flutter3.50.0 内置 Dart3.14.0，13项 Dart 测试通过；不代表移动端原生验收完成。

| 用例 | 验证目标 |
| --- | --- |
| flush preserves category, fields and hides credentials | 分类、结构化 JSON、嵌套凭据与 URL 脱敏，flush 后可读取 |
| minimum level filters records and close drains the last write | 日志级别、关闭等待写入、关闭后拒绝记录 |
| recognizes common JSON credential messages and finite number fields | 常见 JSON 凭据文本脱敏、非有限数字可序列化 |
| serialized file output rotates and retains configured archive count | 大小触发受控轮转，归档份数受限 |
| export creates a snapshot without overwriting user files | 导出独立快照、不中断后续记录 |
| retention deletes only expired archives in an owned directory | 过期归档清理 |
| refuses directories containing unrelated files | 拒绝把用户目录当轮转目录 |
| redacts mixed-case URL schemes in messages fields and stacks | 消息、嵌套字段、堆栈中的大写 HTTPS 凭据/query 脱敏 |
| export rejects dot-segment and symbolic-link aliases of log directory | 实际目录、`..`、符号链接别名均不能导回日志目录 |
| prune failure becomes terminal and close still releases its file | 注入清理失败可观察、保留根因并拒绝后续写入，关闭释放句柄 |
| close / flush / export waits for in-flight rotation without reopening after close | 通过确定性轮转屏障逐项确认生命周期等待和所有文件句柄关闭 |

未覆盖：真实磁盘空间不足、跨 isolate 共享同一路径、系统杀进程与断电持久化。测试注入不是实际磁盘故障验收。
