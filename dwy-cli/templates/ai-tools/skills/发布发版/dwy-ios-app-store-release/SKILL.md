---
name: dwy-ios-app-store-release
description: "Use when 用户要上架、发 iOS/macOS 版本、填 App Store Connect、写更新说明、改关键词或 ASO、处理截图预览图、从现网拷上一版本资料、选过审即发或过审后几天再发、提交 TestFlight 或 App Review。"
---

# iOS/macOS App Store 上架与版本更新

首次上架和后续版本走同一套发布包。后续版本必须先拉现网全部资料，再按本版增量改；禁止从空模板重写。

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

## 判定首次还是更新

将 `assets/appstore-submission.yaml` 复制到 `submissions/<bundle-id>/` 后，用 Bundle ID 查 Connect：

- 没有任何 `appStoreVersions` → `version.source=first`，`screenshots.update=true`
- 已有版本 → `version.source=live_inherit`，按 [api-workflow.md](references/api-workflow.md) 把现网资料整份写入发布包，再优化

## 现网继承

更新时拷过来的字段包括：名称、副标题、描述、关键词、推广文本、更新说明、支持/营销/隐私 URL、截图、价格与地区、内购/订阅、审核备注。先给用户看现网原文，再改本版增量。

## 每版本处理

1. **推广文本不向用户询问**。现网有内容则原样拷进 `promotional_text`。与本版卖点明显不符时自行改写，改前可上网核对卖点是否仍准确；双语各 ≤170 字。首次无现网则按名称/副标题/描述生成。细则见 [aso.md](references/aso.md)。
2. **更新说明**：后续版本 `whats_new` 双语必填。给用户看的概览，写「更新网络抓包功能」这类句子，机制细节不写，可用「等等」。禁止把 `dwy-publish` 的 git `CHANGELOG` 或实现细节贴进商店。首次上架可空。
3. **截图**：默认 `screenshots.update=false`，拷上一版本，不问。仅当本版功能变化很大（新主界面、新核心能力、旧截图已不能代表产品）时，才确认是否按 [screenshot-specs.yaml](references/screenshot-specs.yaml) 更新。
4. **发布策略**：向用户确认二选一——过审即发（`AFTER_APPROVAL`），或过审后几天再发（`SCHEDULED` + `delay_days`）。选几天则再问天数。未选不得提交。

## ASO

名称、副标题、关键词按 [aso.md](references/aso.md) 优化。现网词表为底，补本版可搜词，不重复标题/副标题已覆盖词。输出旧/新关键词和剩余字符数，`aso_confirmed` 后才写。

## 截图规格

P 图与上传只读 [screenshot-specs.yaml](references/screenshot-specs.yaml) 的 `processing.canonical` 与各 display 的 `preferred`。流程见 [screenshot-workflow.md](references/screenshot-workflow.md)。

## 地区、ICP 与本地化

- 默认应用、内购和订阅均为 `all_territories`；产品页本地化仅 `zh-Hans`、`en-US`。
- ICP/APP 备案号为非阻塞字段。缺失时继续配置其它全部地区，并在执行报告标记中国大陆待办。
- 用户后续提供备案号后，单独写入并启用中国大陆；不得重新填写其它已确认资料。

## 自动化顺序

1. 判定 first / live_inherit；更新则先拉现网。
2. 收齐更新说明与 `release.type`；推广文本自处理；截图仅功能变化很大才问；做 ASO，输出完整 diff。
3. 用 API 写入 App 信息、版本本地化、价格、地区、年龄分级、审核资料、截图、内购和订阅。
4. 对 API 未覆盖项复用用户已登录 Playwright 会话：创建 App Record、填写 App Privacy 或处理网页专属确认。
5. 关联构建与审核提交。仅在用户再次确认后调用提交审核或发布动作。
6. 输出成功、失败、待补 ICP 和人工确认项，保存无秘密执行记录。

## 内购与订阅

- 校验 `product_id` 与 StoreKit 代码一致，再创建消耗型、非消耗型内购或自动续期订阅。
- 每个内购必须提交一张审核截图；按 [内购审核截图](references/in-app-purchase-review.md) 从真实购买流程采集并校验。
- 默认全地区可售；以美国区目标价格查询 Apple 价格点，并由 Apple 自动等价换算其它地区价格。
- 价格修改必须展示旧价、新价、生效时间和受影响地区；用户二次确认后才执行。

## 网页自动化限制

- 只使用用户已登录会话，不索取 Apple ID 密码或二次验证码。
- 遇到验证码、实名核验、协议、税务、银行、证照上传或法律声明时暂停并交由用户完成。
- App Review 拒审后整理证据、修复清单与回复草稿；回复或重新提交前确认。

## 参考资料

- API 与现网继承：[references/api-workflow.md](references/api-workflow.md)
- ASO 与字段上限：[references/aso.md](references/aso.md)
- 截图规格（P 图单一数据源）：[references/screenshot-specs.yaml](references/screenshot-specs.yaml)
- 截图流程：[references/screenshot-workflow.md](references/screenshot-workflow.md)
- 内购审核截图：[references/in-app-purchase-review.md](references/in-app-purchase-review.md)
