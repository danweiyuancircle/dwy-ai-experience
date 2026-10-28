# GitHub 仓库公开评估

评估日期：2026-10-28。结论：尚未发现可确认为本项目生产凭据的泄露，但不建议直接将原仓库改为 public。先处理文档凭据、确认个人及业务信息的公开范围，并调整发布检查。

## 检查范围与证据

- GitHub 仓库：`https://github.com/danweiyuancircle/dwy-ai-experience`，实时查询仍为 private，默认分支为 `master`。
- 本地分支：`feat/rightflow-optional-sync`，提交 `b18f8c4`；评估开始时工作区干净。
- 当前跟踪文件共 4,196 个；检查文本内容、3 张 PNG 图片，以及 DOCX 正文。图片检查为可见内容检查，不包含隐藏数据取证。
- 本地不是浅克隆，所有本地引用可达提交共 498 个。远端公布的 90 个引用的目标哈希均已在本地引用目标中找到。
- 使用 Gitleaks 8.30.1，参数为 `git --redact=100 --log-opts="--all --full-history"`。工具报告扫描 484 个提交差异、约 33.44 MB，命中 7 项。工具的提交差异计数与可达提交总数不同，不将二者混用。
- 补充检查常见密钥格式、私钥、带密码的连接串、凭据赋值、个人路径、联系方式，以及发布工作流。
- 当前跟踪文件未发现真实 `.env`、私钥文件、数据库文件或数据库备份；跟踪的 `.npmrc` 只配置 registry，未发现发布 token。
- GitHub 元数据查询返回 0 个 Actions artifact、69 个 Release、105 个 Actions run、0 个 Issue/PR。Release 及日志内容未做完整审计。

## 应先处理的内容

### 1. 第三方文档中的完整凭据

| 当前路径与行号 | 内容 | 判断 |
| --- | --- | --- |
| `dwy-cli/templates/ai-tools/skills/DolphinDB/dwy-dolphindb/references/official/progr/sql/createExternalTable.md:111`、`:112` | 完整 AWS Access Key ID 与 40 字符 Secret Key | 来自第三方公开文档；有效性、权限、归属未知 |
| `dwy-cli/templates/ai-tools/skills/DolphinDB/dwy-dolphindb/references/official/tutorials/Migrate_data_from_InfluxDB_to_DolphinDB.md:114` | 88 字符 InfluxDB token | 来自第三方公开文档；有效性、权限、归属未知 |
| `dwy-cli/templates/ai-tools/skills/DolphinDB/dwy-dolphindb/references/official/tools/superset.md:63` | 固定 Superset SECRET_KEY | 来自第三方公开文档；不应作为可复用部署密钥 |

三个文件均有来源元数据。实时请求来源页面，确认页面仍包含相同的对应凭据值；未尝试用这些凭据访问 AWS、InfluxDB 或 Superset。这不是发现了本项目的生产密钥，也不能证明它们已失效。

来源：[AWS 示例](https://docs.dolphindb.cn/zh/progr/sql/createExternalTable.html)、[InfluxDB 示例](https://docs.dolphindb.cn/zh/tutorials/Migrate_data_from_InfluxDB_to_DolphinDB.html)、[Superset 示例](https://docs.dolphindb.cn/zh/tools/superset.html)。

建议将这些值替换为明确占位符，并检查后续文档同步是否会重新带入。它们从提交 `7e515229` 起已进入历史；只修改当前文件不会从旧提交和旧标签中移除。是否清理这些已经在第三方官网公开的历史示例值，应单独决定；本次未重写历史。

### 2. 其他历史扫描命中

- `backend/packages/webhooks/tests/test_sender_identity.py:59`（提交 `17999c67`）：固定测试签名密钥，按测试上下文判定为测试数据。
- `backend/packages/webhooks/src/dwy_webhooks/reviews/storage.py:149`（提交 `4f0c1129`）：`lease_token=token` 等代码表达式，误报。
- `backend/packages/webhooks/src/dwy_webhooks/delivery.py:105`（提交 `244e99b4`）：`lease_token=token` 等代码表达式，误报。
- 历史路径 `docs/element-plus-dev/docs/.vitepress/config/index.mts:69`（提交 `d241b0d5`）：前端搜索配置中的 Algolia API Key。前端配置通常包含可公开的搜索 key，但本次未验证这个 key 的实际权限，不能据此认定为管理员密钥或保证其无风险。

### 3. 个人与业务信息

- Git 历史作者邮箱使用 `chances.com.cn` 域名；公开仓库会公开相应作者元数据。
- `dwy-cli/CHANGELOG.md:191`、`:193`、`:206` 包含本机用户名及目录结构。建议改为仓库相对路径。
- `backend/docs/email.png` 展示真实品牌“宽舟科技 / QuantZone”及其品牌域名；验证码为示例值 `123456`，未见真实收件人或账户凭据。需确认是否愿意公开这项业务关联。
- `docs/auth-runtime-implementation-report.md` 等文档包含业务项目名称与集成关系；未将这些名称视为密钥，但公开后可被关联。

## 直接改 public 会影响发布

`scripts/private_release.py:22` 的 `require_private_repository()` 查询 GitHub 的实际可见性；第 34–35 行在仓库非 private 时抛出 `refusing to publish or fetch from a public repository`。

以下工作流调用该检查：

- `.github/workflows/publish-admin.yml`
- `.github/workflows/publish-auth-web.yml`
- `.github/workflows/publish-auth.yml`
- `.github/workflows/publish-cli.yml`
- `.github/workflows/publish-device-fingerprint.yml`
- `.github/workflows/publish-eapi.yml`
- `.github/workflows/publish-ekit.yml`
- `.github/workflows/publish-eui.yml`
- `.github/workflows/publish-webhooks.yml`
- `.github/workflows/private-release.yml`

因此需要同步调整检查、相关测试，以及 `AGENTS.md`、`CLAUDE.md`、`README.md`、`README.en.md`、`docs/private-distribution.md` 中的私有源码约定。公开 GitHub 不需要删除根 `package.json` 的 `private: true`；该字段用于防止误发布工作区根包。

## 公开前的剩余检查

1. 清理上述第三方示例凭据并重新扫描；如后续发现自有真实凭据，先撤销或轮换，再决定历史清理方案。
2. 确认作者邮箱、品牌图片及业务文档可以公开，清理本机路径。
3. 调整仓库可见性检查与相关测试，继续保留 GitHub Actions + OIDC 发布方式。
4. 审计保留的 Actions 日志及 Release 附件。GitHub 官方说明，改为 public 后 Actions 历史和日志也会对所有人可见：[仓库可见性说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)。
5. 根目录没有统一 LICENSE，GitHub 查询的 `licenseInfo` 为空；部分包声明 MIT。尚未核验整库第三方文档及图片的再分发授权，不将“可见性公开”视为已经完成整库许可证整理。

本次仅评估并生成报告，没有修改代码、凭据、Git 历史或仓库可见性，没有验证凭据可用性，也未完整审计 Actions 日志和 Release 附件。正则及 Gitleaks 扫描不能证明绝对不存在敏感数据。
