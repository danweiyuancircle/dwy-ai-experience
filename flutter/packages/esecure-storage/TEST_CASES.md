# dwy_secure_storage 测试

入口：`test/secure_storage_test.dart`。

| 用例 | 验证 |
| --- | --- |
| round trips secrets and removes a single key | 缺失返回 null、读写与单键删除 |
| clear preserves other accounts, products and native keys | 本域清理不调用 deleteAll，不删除其他账号/产品/native 键 |
| scope encoding cannot collide through separators | 分段编码隔离点号等分隔符组合 |
| invalid names are rejected and platform failures propagate | 无效输入拒绝，平台锁定/写入失败不被吞掉 |

2026-11-16：Flutter3.50.0 / Dart3.14.0，4项测试通过。插件替身不证明平台加密和真机锁屏行为。
