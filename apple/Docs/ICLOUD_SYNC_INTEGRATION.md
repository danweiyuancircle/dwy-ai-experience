# AppleAppKit iCloud 设置同步整合

首个交付服务 RightFlow 下一版，只围绕 RightFlow 的菜单和偏好配置整合源码。当前 RightFlow 1.0 继续使用本机设置。共享库接口以首个实际接入验证为准。

## 上游源码

以下三份源码均按精确版本或提交独立检出，保留 Git 历史和原始 MIT 许可证。

| 上游 | 源码基线 | 用途 |
| --- | --- | --- |
| [Defaults](https://github.com/sindresorhus/Defaults/tree/9.0.9) | `9.0.9` · `00a7465a0668a87fa159e779b9d80f1f9652357e` | 参考按键启用同步、自定义 UserDefaults suite、本机变更观察与回写去重。其时间戳策略会采用较新的修改，适合可覆盖的独立偏好。 |
| [CloudStorage](https://github.com/nonstrict-hq/CloudStorage/tree/0.7.0) | `0.7.0` · `d94cb14e563c1a20edeba8a861395c60c2b9d064` | 优先评估 `CloudStorageSync` 的 KVS 读写和外部变更通知。由团队模块决定何时应用整套配置，以及何时让用户选择。 |
| [Apple CKSyncEngine 示例](https://github.com/apple/sample-cloudkit-sync-engine/tree/63d9d16d75429a94d06d77f6dac13cb9a777b09f) | `63d9d16d75429a94d06d77f6dac13cb9a777b09f` | 保留为后续应用数据同步的参考。 |

实际纳管时按 `apple/ThirdParty` 现有方式记录上游 URL、tag、完整 commit、许可证与团队补丁。只选当前用到的一套 iCloud 读写实现，配置类型、生命周期和冲突行为使用团队接口。升级时先拉取独立上游，评审差异后重放团队补丁，再由消费 App 验证。

## RightFlow 首个接入

拟由 AppleAppKit 封装 iCloud KVS 的读写、变更观察和恢复流程。RightFlow 定义允许同步的 `Codable` 配置、版本迁移和本机设置的应用方式。路径、沙盒书签、Finder 扩展开关和默认解压关联由本机管理。

1. 主应用在用户开启同步后读取 iCloud。已有云端配置、且本机没有自定义设置时恢复。两边已有配置时先展示选择。第一份云配置由用户明确从本机备份。启动阶段读到空值时保留当前设置，等待初始同步。 [Apple 初始同步事件](https://developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestoreinitialsyncchange)
2. 将动作开关、排序、自定义名称和外观编码为一份带版本的快照。本机保存成功后合并短时间内的多次修改，再提交 iCloud。主应用收到有效版本后写回 App Group，Finder 扩展继续读本机数据。迁移器负责已有配置和未知字段的处理。
3. 记录上一次采用的版本和本机待同步内容。发现双方都改过时保留本机配置和云端候选，由用户选择采用哪套。KVS 提供的是异步键值同步，界面以本机保存和收到云端更新作为可验证状态。 [Apple 设置同步文档](https://developer.apple.com/documentation/foundation/synchronizing-app-preferences-with-icloud)
4. 切换 Apple 账户时暂停旧同步会话，保留未上传修改，待用户确认后接入新账户。配置解码和配额异常时保留原有本机配置。 [Apple 账户变更事件](https://developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestoreaccountchange)

## 接入验收

- 用测试替身覆盖首次恢复、本机离线编辑、可识别的双端冲突、切号隔离、旧版解码和远端更新回写去重。
- 用签名的 RightFlow 在两台 Mac 上验证备份、菜单恢复、Finder 生效和目录重新授权。

## 后续参考

其他应用和应用数据同步按实际需求另行排期。已有 AppCloud 账号的应用可参考 `apple/Docs/SYNC_CORE.md`。需要 Apple 账户下的用户记录同步时，再评估 CloudKit 私有数据库和上游示例。 [Apple CKSyncEngine 文档](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5)

当前交付为上游源码检出和接入设计。共享 API、云端配置和首个 App 接入待实施。
