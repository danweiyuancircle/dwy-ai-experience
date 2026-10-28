# dwy-webhooks：共享迁移与外部注入

## 已确认目标

通用 Webhook 能力由 dwy-shared 维护，独立分发为 `dwy-webhooks`，依赖 EAPI。业务项目只安装模块、注入配置与资源、注册一次入口；不能复制 App Cloud 的配置类、数据库或业务包。用户明确要求配置由外部注入。

## 落地边界

- `backend/packages/webhooks`：Discord 发送、Resend/ASC/Apple 通知适配器、事件契约、可注入接收器和 SQLAlchemy 投递队列。
- `WebhookConfig` 是纯 Pydantic 模型，不读取环境或 dotenv；Apple 根证书仅接收外部字节，不读取证书文件。
- EAPI 提供异常基础、日志与接入项目的数据库资源工厂；Webhook 模块不配置 EAPI 的全局环境、缓存或数据库。
- 核心依赖 EAPI；Discord/Resend/Apple SDK 以 extras 隔离。基础包不要求安装这些 SDK。
- `install_webhooks(app, config, sinks=..., receipts=...)` 是项目集成入口；`create_app(config)` 明确要求配置。
- SQL 队列由项目注入 sessions、table、sender、source 和策略；不创建/迁移/关闭项目数据库。默认同步转发仅提供实例内有界去重，不宣称持久投递。
- App Cloud 保留配置映射、legacy ASC 表登记和薄适配器；旧表名、列、长度、主键和公开 URL 不变。Apple 商品/账户/权益留在业务包。

## 实现与验证顺序

1. 迁移已有草稿并将包名统一为 dwy-webhooks；先增加显式注入失败测试。
2. 拆除环境与证书文件读取；通用错误/日志复用 EAPI；SDK 按需导入。
3. 把所有提供方的验签/解析放进共享包，抽出可注入的 SQL 队列，App Cloud 只映射与注册。
4. 更新共享 CI/分发登记、项目预览构建、锁文件和独立应用 wheel 验收。
5. 使用全新环境、真实非 editable wheel，在业务包全部缺席时验证配置、注册、提供方路由与默认转发。

## 已观察的回归与收口

- 显式注入契约最初因缺少共享包而失败；旧环境配置加载被移除后通过。
- 独立 ASGI 工厂起初返回默认 FastAPI 错误，已测试失败并接入 EAPI 错误处理；注册入口不覆盖宿主已有处理器。
- 代码复核复现静态路由遮蔽 `{app_id}` 模板；新增失败用例后按路径形状拒绝重叠。
- 公共 HTTP 身份已从 App Cloud 改为 dwy-webhooks，回归断言同步。
- 最终共享源码 80 项测试及 Ruff 通过；复核确认上述两项问题已解决。

## 发布边界

本轮构建独立 wheel、配置 CI 与 OIDC 发布工作流，并在 App Cloud 本地消费实际产物。没有提交、推送、发布包、部署生产或发送真实第三方通知。源码和 wheel/示例验收不能代替真实商店/邮件/购买事件的线上验收。

## 最终验收证据

- 最终 `dwy_webhooks-0.1.0` wheel SHA-256：`2689a0269fbc299572092da3eb64971f1e71f9167998312b890fa10cb1c7e716`。
- 全新 full 环境仅安装本轮 EAPI、Webhook wheel 及选定 extras/测试依赖；临时项目 cwd、`python -I`、无 PYTHONPATH，80 项测试通过。模块来自新环境 site-packages，App Cloud、Apple IAP、cloud-kernel、dwy-auth、旧 cloud-webhooks 和产品包全部缺席。
- core-only 新环境未安装 Discord、Resend、Apple SDK，仍可导入配置及注册 API，创建无平台配置的 FastAPI 应用。
- 原样示例项目通过外部配置注入、Resend 真实签名/去重/无签名拒绝、ASC HMAC ping、自定义路径、离线 Discord 发送、邮件主题不转发和自身 status 端点测试。
- Apple 有效事件路径在官方 SDK 验签边界使用离线替身，同时验证真实 SDK 拒绝伪造签名、嵌套 JWS 关系、取消预算与关闭；本轮没有发送真实 Apple/Discord/Resend 通知。
- App Cloud 完整本地脚本通过前端测试/build与三应用独立 wheel 验收。评审修复后，最终安装产物再执行后端全量：503 passed、13 skipped；跳过项要求真实 PostgreSQL 测试连接或本机 nginx。
- 两仓库相关 Ruff、diff check 通过；发布登记/预览构建契约 12 passed、22 subtests passed。两个评审问题已按失败测试→修复→独立复核收口。
