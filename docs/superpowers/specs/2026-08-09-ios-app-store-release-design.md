# iOS App Store Release Skill 设计

## 目标

在 dwy 的 AI 工具模板中提供一个跨工具同步的 iOS/macOS App Store 上架 Skill。它以 App Store Connect API 为主、已登录网页自动化为补充，收集并确认上架信息后生成可审计发布包，并在授权范围内完成填充。

## 位置与秘密

- 模板目录：`dwy-cli/templates/ai-tools/skills/发布发版/dwy-ios-app-store-release/`。
- 用户私有目录：`/Users/chances/.dwy/app-store-connect/`；保存 API 配置、私钥、会话状态和发布包，不能提交到仓库。
- Skill、项目仓库、Git 和发布包禁止写入 API 私钥、审核密码或浏览器 Cookie。

## 发布模型

- 产品页仅使用 `zh-Hans` 与 `en-US`；应用与内购默认全部 App Store 地区可售。
- 中国大陆 ICP/APP 备案号是非阻塞字段。缺失时继续填充所有其它信息并记录待办；收到备案号后单独启用中国大陆。
- iOS 与 macOS 的截图分平台、分尺寸、分语言采集、校验和上传。
- 内购覆盖消耗型、非消耗型与自动续期订阅，定价采用美国区价格点和 Apple 自动等价换算。
- API 覆盖的字段优先 API 写入；只有 API 无法完成的 App Record、隐私问卷等页面使用已登录 Playwright 会话。

## 安全与确认

- 首次运行询问 Issuer ID、Key ID、私钥位置、团队和默认偏好，并仅写入用户私有目录。
- 执行前输出 diff；提交审核、发布、价格上调必须再次获得用户确认。
- 隐私、内容权利、加密、税务、备案和实名材料只由用户确认真实性；Skill 只整理资料与执行已确认动作。

## 组成

- `SKILL.md`：工作流、确认门禁、API/网页边界。
- `scripts/appstore_config.sh`：创建、读取和重置用户私有 API 配置；不接收或打印私钥内容。
- `assets/appstore-submission.yaml`：发布包骨架。
- `references/screenshot-workflow.md`：真实应用截图采集和平台规格校验。
- `references/api-workflow.md`：App Store Connect API、Playwright 和上架顺序。

## 验证

- 先用 shell 测试验证私有配置初始化、权限收紧、读取和重置行为。
- 运行 Skill Creator 的结构校验。
- 用 `bash -n` 验证脚本语法，并通过模板检查确认没有私钥或审核密码字段。
