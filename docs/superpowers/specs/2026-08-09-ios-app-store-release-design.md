# iOS App Store Release Skill 设计

## 目标

在 dwy 的 AI 工具模板中提供一个跨工具同步的 iOS/macOS App Store 上架 Skill。首次上架与后续版本同一套发布包。后续版本必须先拉现网全部资料，再按本版增量优化（ASO、推广文本、更新说明、截图开关、过审后发布策略）。

## 位置与秘密

- 模板目录：`dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/`。
- 用户私有目录：`/Users/chances/.dwy/app-store-connect/`；保存 API 配置、私钥、会话状态和发布包，不能提交到仓库。
- Skill、项目仓库、Git 和发布包禁止写入 API 私钥、审核密码或浏览器 Cookie。

## 发布模型

- 产品页仅使用 `zh-Hans` 与 `en-US`；应用与内购默认全部 App Store 地区可售。
- 中国大陆 ICP/APP 备案号是非阻塞字段。缺失时继续填充所有其它信息并记录待办；收到备案号后单独启用中国大陆。
- 已有版本：`version.source=live_inherit`，从 `READY_FOR_SALE`（或最新版本）拷贝本地化、截图、价格、内购和审核备注，禁止空模板重写。
- 每版本：推广文本不向用户询问（现网有则继承，需更新时自改并可上网核对）；后续版本的用户向更新说明必填；截图默认拷上版，仅功能变化很大才确认是否更新；`release.type` 为 `AFTER_APPROVAL` 或 `SCHEDULED`（过审后几天再发）。
- 更新说明写概览，不写实现；不使用 git `CHANGELOG`。
- ASO 以现网名称/副标题/关键词为底，关键词不重复已覆盖词，100 字上限。
- 截图尺寸只以 `references/screenshot-specs.yaml` 为准；后续 P 图读同一文件。iOS 与 macOS 分平台出图。
- 内购覆盖消耗型、非消耗型与自动续期订阅，定价采用美国区价格点和 Apple 自动等价换算。
- API 覆盖的字段优先 API 写入；只有 API 无法完成的 App Record、隐私问卷等页面使用已登录 Playwright 会话。API 创建新版本不会自动带旧资料，截图在 `update=false` 时必须拷到新版本。

## 安全与确认

- 首次运行询问 Issuer ID、Key ID、私钥位置、团队和默认偏好，并仅写入用户私有目录。
- 执行前输出 diff；提交审核、发布、价格上调必须再次获得用户确认。
- 提交前确认「过审即发」或「过审后几天再发」；后者写入 `SCHEDULED` + `delay_days`。
- 隐私、内容权利、加密、税务、备案和实名材料只由用户确认真实性；Skill 只整理资料与执行已确认动作。

## 组成

- `SKILL.md`：工作流、确认门禁、API/网页边界。
- `scripts/appstore_config.sh`：创建、读取和重置用户私有 API 配置；不接收或打印私钥内容。
- `assets/appstore-submission.yaml`：发布包骨架（`schema_version: 2`）。
- `references/api-workflow.md`：现网继承、API 写入、Playwright 补齐。
- `references/aso.md`：字段上限与关键词规则。
- `references/screenshot-specs.yaml`：预览图像素与 P 图契约（单一数据源）。
- `references/screenshot-workflow.md`：采集、是否更新、上传前检查。
- `references/in-app-purchase-review.md`：内购审核截图。

## 验证

- 先用 shell 测试验证私有配置初始化、权限收紧、读取和重置行为。
- 模板测试覆盖现网继承、推广文本、更新说明、发布策略、截图规格与 ASO。
- 用 `bash -n` 验证脚本语法，并通过模板检查确认没有私钥或审核密码字段。
