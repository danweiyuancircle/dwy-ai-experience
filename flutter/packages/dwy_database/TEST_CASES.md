# dwy_database 测试

入口：`test/database_test.dart`，schema 示例：`example/note_database.dart`。

| 用例 | 验证 |
| --- | --- |
| file data survives close and reopening; close is idempotent | 真实文件重开保留记录，重复 close 共用 Future，关闭后拒绝新访问 |
| transaction failure rolls back instead of leaving a partial write | 事务异常后无部分写入 |
| product query stream observes committed writes | 初始空结果及提交后的真实 query stream 更新 |
| migration preserves old records and adds default values | v1→v2 保留正文并增加默认 false 字段 |
| failed migration closes resources without erasing existing records | 升级失败以 DriftRemoteException 保留原错误，原文件可由旧 schema 重开，记录保留 |

2026-11-16：Flutter3.50.0 / Dart3.14.0，官方 build_runner 生成成功，5项测试通过。Flutter 真机文件目录、原生产物与退出等待需另行验收。
