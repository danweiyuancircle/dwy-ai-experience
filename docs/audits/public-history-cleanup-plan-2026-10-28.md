# 公开前历史脱敏执行计划

状态：当前工作树的文档占位符、发布访问检查及说明已修改；临时镜像的历史清理验证通过。尚未重写远端、移动远端标签或修改仓库可见性。

## 已完成的准备

- 当前 3 份 DolphinDB 文档中的 AWS Access Key ID / Secret Key、InfluxDB token、Superset SECRET_KEY 已替换为明确的 `YOUR_...` 占位符。
- `scripts/private_release.py` 保留 GitHub API 访问和响应校验，允许 public/private 两种可见性；网络失败或无效响应仍中止发布。
- 同步发布工作流的检查名称，以及当前 README、项目约定、分发文档和 `scripts/tests/TEST_CASES.md`。
- 在 `ci` 锁定环境运行 `scripts/tests`：20 项通过；相关 Python 文件 Ruff 通过；真实仓库访问检查和 `git diff --check` 通过。系统 Python 直接运行全部脚本测试时，独立虚拟环境探针用例失败；使用项目 CI 环境后通过。
- 当前 4,196 个跟踪文件重新扫描后，Gitleaks 只剩 3 项已核对的测试/代码误报，详见原始评估报告。

## 历史清理的具体范围

只按已确认的 5 个完整值做精确替换，不删除源文件或提交，不改业务代码：

| 凭据 | 替换值 |
| --- | --- |
| AWS Access Key ID | `YOUR_AWS_ACCESS_KEY_ID` |
| AWS Secret Access Key | `YOUR_AWS_SECRET_ACCESS_KEY` |
| InfluxDB token | `YOUR_INFLUXDB_TOKEN` |
| Superset SECRET_KEY | `YOUR_RANDOM_SUPERSET_SECRET_KEY` |
| 历史 Algolia API Key | `YOUR_ALGOLIA_SEARCH_API_KEY` |

临时镜像使用 `git-filter-repo` 验证，匹配规则仅保存原值 SHA256，不把原始密钥写入清理脚本。自检确认 5 个值均被替换，其他内容保持不变。清理后 Gitleaks 全引用历史扫描只剩同样的 3 个误报。

已核对的远端影响：

- 4 个分支：`master`、`feat/auth-runtime`、`feat/rightflow-optional-sync`、`release/shared-ui-audit-20261023`。
- 85 个远端标签均需要更新其目标对象。
- 本地完整镜像中的 375 个提交哈希会改变；不能把这个本地全引用计数当作远端独立提交总数。
- 当前功能分支与 `master` 已分叉；公开准备改动还需按各分支当前文件同步，不能靠重写历史自动传播代码修改，也不应因此合并无关功能。

## 需要明确授权的操作

重写远端分支、移动已发布标签和删除历史附件属于破坏性操作，不包含在普通文档替换中。执行前须授权这一具体范围；已经获得的 public 授权无需重复确认。

授权后按以下顺序执行：

1. 保存原始 refs、完整 Git bundle 和现有 Release 附件，保存在仓库外的本地私有备份中，不推送为远端备份分支或标签。
2. 基于最新远端重新核对清理结果，保留其他会话的提交和工作区改动；将公开准备补丁同步到默认分支及相关活跃分支，完成必要测试。
3. 根据逐引用的旧哈希，使用明确的 refspec 和 `--force-with-lease` 更新受影响的 4 个分支和 85 个标签；禁止 `push --mirror` 带上本机临时或 Codex 引用。
4. 检查并处理含旧凭据的 Release 附件；不静默重建同版本包冒充原始不可变产物，也不篡改原始 SHA256 清单。
5. 再次扫描远端可达历史并确认旧值未被重新引入，然后执行已授权的 public 切换并验证匿名读取。

## 风险及验收边界

- SwiftPM/Xcode 的 `Package.resolved` 可能锁定旧提交，标签移动后需重新解析。其他克隆需要迁移到新历史，不能合并旧历史重新带入原值。
- 依赖提交或标签对象的签名、历史发布记录中的 revision 会与新对象不一致。既有公开 npm/PyPI 包不能被这次 Git 历史清理追溯修改。
- 已确认 69 个 GitHub Release 中有两份 CLI 附件：`0.6.0` 下的 `create-dwy-0.21.0.tgz`，以及 `0.4.1` 下的 `create-dwy-0.20.0.tgz`。两份附件尚在下载，已收到的压缩数据解码后均命中已知 AWS 密钥值；`0.20.0` 的已收数据还命中 InfluxDB token。因此已确认两份附件也需要处理，但尚未完成原始附件的完整备份与校验。
- 最新 3 次 Actions run 的日志已抽查，常见密钥格式未命中。两次扩大批量的审查超时，没有留下完整结果，不能宣称已审完 105 次运行。
- 仅重写 refs 不保证旧对象从 GitHub 缓存消失。完全清除缓存引用可能需要 GitHub Support；这与替换可达历史是不同的验收项。见 [GitHub 敏感数据清理说明](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)。
- 本计划不包含删除整个仓库、发布新 npm/PyPI 版本、改变包版本号或向第三方发送消息。
