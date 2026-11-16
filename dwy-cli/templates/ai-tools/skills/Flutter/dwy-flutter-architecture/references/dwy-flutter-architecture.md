# Flutter 四层、共享包与代码抽取

采用与团队 Apple 项目相同的职责边界；Dart 目录使用 snake_case。四层是归属和依赖约束，不要求每个目录都成为独立 package。

| 层 | 产品中的位置 | 责任 |
| --- | --- | --- |
| Assembly | `lib/app/` | 入口、配置、路由挂载、DI、生命周期 |
| Features | `lib/features/<feature>/` | 可独立裁剪的业务功能、页面和状态持有者 |
| BizFoundation | `lib/biz_foundation/` | 当前产品跨 Feature 的业务模型、Repository 和服务 |
| Foundation | 共享包；产品 `lib/foundation/` 记录接入/必要适配 | 换一个产品仍可复用的能力 |

依赖：Assembly → Features / BizFoundation / Foundation；Features → BizFoundation / Foundation；BizFoundation → 非 UI Foundation。Foundation 不反向依赖产品。Feature 互引为零，跨域由协议或 Assembly 协调。

## 与官方架构的关系

先读取官方 [flutter-apply-architecture-best-practices](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-apply-architecture-best-practices/SKILL.md)。官方的 View/ViewModel、Repository/Service 描述对象职责；DWY 四层描述代码归属，两者不是竞争的目录模板。参考 [Flutter 官方架构指南](https://docs.flutter.dev/app-architecture/guide)。

- 页面及其状态归 Feature；被多 Feature 使用的产品 Repository 归 BizFoundation。
- 业务依赖接口/基础能力，不依赖 BuildContext、Widget、主题和应用路由。
- Flutter 插件包可能无自定义 UI，但仍需要 Flutter 引擎和平台配置；不能把“无 UI”写成“纯 Dart”。
- 不建万能 `core/shared/AppShared` 收纳业务会话、路由、页面和工具；不为套四层给组件 Gallery 创建空业务包。
- 产品 schema、DTO、认证/离线策略不自动进入跨产品共享包。基础库复用代码，不混用账户、数据库或会话。

## 共享包与消费

- Dart 包独立于 Widget；Flutter UI 和平台插件按需依赖。禁止一个聚合入口强制引入网络、数据库、相册和全部 UI。
- 先查共享包公开 API、已发布版本和验收状态；新增封装优先成熟依赖，不自研传输、加密、ORM 或图片缓存引擎。
- workspace 使用官方 Pub workspaces。每个成员声明直接依赖，统一解析及锁文件；纯 Dart 和 Flutter 测试依赖需一起核对。
- 同仓联调可用 workspace；跨仓消费使用正式发布包或明确 Git 版本，不把本机绝对 path 依赖提交到产品。
- 新宿主用官方 CLI 生成；SDK、原生插件 minOS、原生工程 deployment target、CI 矩阵同步核对。
