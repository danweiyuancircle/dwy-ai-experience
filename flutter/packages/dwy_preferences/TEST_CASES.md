# dwy_preferences 测试

入口：`test/preferences_test.dart`。

| 用例 | 验证 |
| --- | --- |
| typed keys round trip and missing values stay absent | 五种类型读写、缺失为 null、单键删除、列表与调用方隔离 |
| clear only removes keys belonging to exact product and scope | 清理只传当前域的 allowList，保留其他 scope/product/native 设置 |
| reads observe backend changes instead of a private cache | 后端变化可在下次读取观察到 |
| scope separators do not collide and wrong stored types are rejected | 分段命名空间不串数据，已有类型不匹配时抛错 |
| backend failures propagate and invalid keys fail before a write | 空作用域/键拒绝，写失败不伪造成功 |

2026-11-16：Flutter3.50.0 / Dart3.14.0，5项测试通过。真实磁盘和多引擎行为不由内存替身测试证明。
