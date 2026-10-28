# 公开仓库脱敏执行结果

日期：2026-10-28。

仓库 `https://github.com/danweiyuancircle/dwy-ai-experience` 已改为 public。GitHub API 返回 `private: false`，未携带身份的仓库 API 与默认分支源码访问均返回 HTTP 200。

## 已完成

- 将完整 AWS Access Key ID / Secret Key、InfluxDB token、Superset SECRET_KEY、历史 Algolia API Key 替换为明确的 `YOUR_...` 占位符。它们来自第三方示例或历史前端配置，未尝试验证其权限或有效性。
- 对远端 4 个分支和 85 个标签完成历史脱敏。推送前逐项校验旧哈希，使用 `--atomic` 和逐引用 `--force-with-lease`；推送后 89 个远端引用全部与已扫描镜像一致。
- 检查 89 个引用可达历史中 9,719 个不超过 3 MB 的 blob，总计约 56.22 MB，5 个已知完整值命中数为 0。Gitleaks 全引用历史扫描只剩 3 个已核对的测试/代码误报，没有新增未解释的命中。
- 在各分支原有代码基础上调整发布访问检查，未合并无关业务功能。当前功能分支的脚本测试 20 项通过，其他 3 个分支各 9 项通过；相关 Python 文件 Ruff 全部通过。
- 完整备份并撤下 `0.6.0` 的 `create-dwy-0.21.0.tgz`、`0.4.1` 的 `create-dwy-0.20.0.tgz`，撤下后匿名附件 API 均返回 HTTP 404。其他附件与原始校验清单保留，Release 说明已明确历史快照集合不再完整。
- 原始 Git bundle 验证为完整历史，两份 CLI 原始文件的大小和 SHA256 与 GitHub 记录一致。备份位于仓库外的 Codex 私有备份目录 `dwy-shared-public-20261028`，目录权限为 `700`，未上传备份引用。
- 更新历史标签期间暂停 Actions，完成后恢复 `enabled: true`、`allowed_actions: all`、`sha_pinning_required: false`。核对运行总数仍为 105，没有重触发旧标签发布。
- 当前工作分支已切换到脱敏后的等价文件树，使用 soft reset 保留文件和索引；其他会话的工作树未重置。

## 尚未完成及使用注意

- **GitHub 旧提交缓存仍可读取。** 实测按原始提交 SHA 请求旧文件返回 HTTP 200，仍含原 AWS 示例值。分支、标签不可达不等于平台旧对象已彻底删除；完全清除需要 GitHub Support 协助。本报告不公开具体旧缓存链接或密钥值，支持请求草稿保存在仓库外私有备份中，尚未发送。
- Actions 历史日志仅抽查最新 3 次，未完成 105 次日志的完整审计；不以本次 Git 扫描证明日志绝无敏感内容。
- 其他本地克隆和工作树须迁移到新历史，禁止直接合并旧历史后推回；SwiftPM/Xcode 锁定旧提交时需重新解析依赖。
- 本轮未发布新的 npm/PyPI 包，不能追溯修改已经分发出去的包或第三方官网示例。
- 根目录统一许可证及第三方文档、图片授权未在本轮整理。

GitHub 对旧提交缓存、其他克隆及平台清理的边界说明见：[Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)。

