---
name: dwy-ios-app-store-release
description: "iOS/macOS App Store 上架编排。用户要求创建或填写 App Store Connect 应用资料、生成并上传 iOS/macOS 截图、配置全地区定价、创建内购/自动续期订阅、提交 TestFlight 或 App Review 时使用。使用 App Store Connect API 自动填充，使用已登录 Playwright 补齐网页专属步骤；首次运行在用户私有目录缓存 API 配置。"
---

# iOS/macOS App Store 上架

将开发完成的 Apple 应用整理为可确认、可审计、可重复执行的发布包。API 优先；新建 App Record、App Privacy 等 API 外页面才使用已登录 Playwright。

## 安全边界

- Skill 模板目录禁止保存任何 API Key、`.p8` 私钥、Cookie、审核账号密码或税务材料。
- 只从 `/Users/chances/.dwy/app-store-connect/` 读取用户私有配置。首次运行时询问 Issuer ID、Key ID、团队和私钥文件位置，再调用 `scripts/appstore_config.sh` 写入。
- 不将秘密写入项目、Git、`appstore-submission.yaml` 或执行日志。审核账号在发布包中只能使用钥匙串或环境变量引用。
- 提交审核、正式发布、价格上调前，必须显示变更并获得用户二次确认。

## 首次配置

1. 执行 `scripts/appstore_config.sh init`，创建权限 `0700` 的用户私有目录。
2. 逐项询问用户，再执行 `set --issuer-id <id> --key-id <id> [--team-id <id>]`。
3. 用户提供现有 `.p8` 文件路径后，执行 `import-key --path <absolute-path>`；禁止让用户在聊天中粘贴私钥内容。
4. 使用 `get` 验证非秘密标识；不要打印私钥或会话文件。

## 发布包与资料收集

将 `assets/appstore-submission.yaml` 复制到用户私有目录下 `submissions/<bundle-id>/`，逐步收集并在每步确认：

1. 应用身份：Bundle ID、SKU、名称、分类、版权、年龄分级和构建。
2. 产品页：只维护 `zh-Hans`、`en-US` 的名称、副标题、描述、关键词、支持/营销/隐私 URL。
3. 截图：按 [截图工作流](references/screenshot-workflow.md) 从真实应用采集 iOS 与 macOS 图，分别校验后上传。
4. 合规：隐私、第三方 SDK、内容权利、加密、审核账号和测试路径。法律真实性由用户确认。
5. 商业：应用价格、全地区可售、内购或订阅的权益、价格、地区和审核截图。

## 地区、ICP 与本地化

- 默认应用、内购和订阅均为 `all_territories`；产品页本地化仅 `zh-Hans`、`en-US`。
- ICP/APP 备案号为非阻塞字段。缺失时继续配置其它全部地区，并在执行报告标记中国大陆待办。
- 用户后续提供备案号后，单独写入并启用中国大陆；不得重新填写其它已确认资料。

## 自动化顺序

1. 读取发布包、项目构建信息和 API 配置，先输出完整 diff。
2. 用 API 写入 App 信息、版本本地化、价格、地区、年龄分级、审核资料、截图、内购和订阅。
3. 对 API 未覆盖项复用用户已登录 Playwright 会话：创建 App Record、填写 App Privacy 或处理网页专属确认。
4. 关联构建与审核提交。仅在用户再次确认后调用提交审核或发布动作。
5. 输出成功、失败、待补 ICP 和人工确认项，保存无秘密执行记录。

## 内购与订阅

- 校验 `product_id` 与 StoreKit 代码一致，再创建消耗型、非消耗型内购或自动续期订阅。
- 默认全地区可售；以美国区目标价格查询 Apple 价格点，并由 Apple 自动等价换算其它地区价格。
- 价格修改必须展示旧价、新价、生效时间和受影响地区；用户二次确认后才执行。

## 网页自动化限制

- 只使用用户已登录会话，不索取 Apple ID 密码或二次验证码。
- 遇到验证码、实名核验、协议、税务、银行、证照上传或法律声明时暂停并交由用户完成。
- App Review 拒审后整理证据、修复清单与回复草稿；回复或重新提交前确认。

## 参考资料

- API 与网页动作：见 [references/api-workflow.md](references/api-workflow.md)。
- iOS/macOS 截图采集与规格：见 [references/screenshot-workflow.md](references/screenshot-workflow.md)。
