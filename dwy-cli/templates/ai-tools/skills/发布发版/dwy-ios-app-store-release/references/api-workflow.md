# App Store Connect API 与网页补齐

## API 优先动作

使用 App Store Connect API 创建或更新版本本地化、App 信息、分类、年龄分级、地区可售性、应用价格、内购、订阅、审核资料、截图和审核提交。每次写入前读取当前资源并生成字段 diff。

## 现网继承（`source=live_inherit`）

Connect 上已有该 Bundle ID 的版本时必须走这条路径。禁止从空模板重写产品页。API 创建新版本不会自动带上旧资料，要自己拷。

1. `GET /v1/apps?filter[bundleId]=`
2. `GET /v1/apps/{id}/appStoreVersions?filter[appStoreState]=READY_FOR_SALE`。没有在售版本时，改取最新一条（`PREPARE_FOR_SUBMISSION` / `WAITING_FOR_REVIEW` / `PENDING_DEVELOPER_RELEASE` / `REJECTED`）。
3. `GET /v1/appStoreVersions/{id}/appStoreVersionLocalizations` → `promotionalText`、`whatsNew`、`description`、`keywords`、`supportUrl`、`marketingUrl`
4. `GET /v1/apps/{id}/appInfos` 与 `appInfoLocalizations` → `name`、`subtitle`、`privacyPolicyUrl`
5. `GET` 各本地化的 `appScreenshotSets` / `appScreenshots`（含 `imageAsset`）
6. `GET` 价格、地区、内购、订阅、审核备注
7. 写入 `submissions/<bundle-id>/appstore-submission.yaml`：`source=live_inherit`，`inherited_from=<现网 versionString>`，其它字段填现网原文
8. 先展示现网原文，再只改本版增量：`whats_new`、ASO、`release.type`。推广文本默认原样继承，仅卖点过时时自改。截图默认拷现网，仅功能变化很大才问是否更新

`source=first` 仅当第 1 步找不到 App，或 App 还没有任何 `appStoreVersions`。

本地发布包 `schema_version` < 2 时：保留已确认的 ICP/内购/审核引用，按现网补齐 `version` 段（含推广文本、更新说明、截图开关、发布策略），再升到 2。不要对着旧骨架继续填。

## 新版本写入

1. `POST /v1/appStoreVersions` 创建 `version_string`
2. 按发布包把上一版本本地化 `POST` 到新版本，再 PATCH 本版改动（推广文本、更新说明、关键词等）
3. 截图：`screenshots.update=false` 时下载现网各 `displayType` 图，在新版本重建 screenshot set 并上传。禁止空截图集提交。`update=true` 时按 [screenshot-specs.yaml](screenshot-specs.yaml) 处理后上传
4. `PATCH` 新版本 `releaseType`：`AFTER_APPROVAL`，或 `SCHEDULED` 且写入 `earliestReleaseDate`（提交时刻 + `delay_days`，UTC）。未写入不得提交
5. 关联构建。提交审核、正式发布、涨价仍走最终门禁

## 网页补齐动作

只在 API 无法覆盖时，使用用户已登录的 Playwright 会话：创建 App Record、App Privacy 问卷和 Apple 要求的网页专属确认。不得自动绕过验证码或复用未授权会话。

## 中国大陆

默认请求全地区可售。若 Apple 返回 ICP 缺失或无效状态，保留其它地区配置并在执行记录中登记备案待办。用户提供有效备案号后，单独重试中国大陆。

## 最终门禁

下列动作必须再次询问用户：提交审核、正式发布、提高价格、启用中国大陆（当备案资料刚补齐时）。

`release.type=AFTER_APPROVAL`：提交前确认「审核通过即发布」。
`release.type=SCHEDULED`：提交前确认「审核通过后等 N 天再发」，并把 `delay_days` 换成 `earliestReleaseDate`。若实际过审日晚于该日期，Apple 会在过审时发布。
