# Flutter 四层边界

沿用 Apple 基础架构的职责：Assembly、Features、BizFoundation、Foundation。目录不等于独立包，不为形式拆包。

| 层 | 归属 | 约束 |
| --- | --- | --- |
| Assembly | 产品 `lib/app/` | 启动、路由、注入、生命周期、主题挂载，不写业务规则 |
| Features | 产品 `lib/features/<feature>/` | 按业务域聚合页面、状态和专属逻辑；Feature 之间不直接引用 |
| BizFoundation | 产品 `lib/biz_foundation/` | 本产品跨 Feature 共享的业务模型、Repository 和会话；不依赖 Widget、路由或设计主题 |
| Foundation | 共享仓库 `flutter/packages/` | 跨产品复用基础包；不包含产品实体、权限决策或业务导航 |

依赖：Assembly → Features / BizFoundation / Foundation；Features → BizFoundation / Foundation；BizFoundation → 非 UI Foundation 包。Foundation 不反向引用产品。

`dwy_design` 属于 Foundation，但只供 Assembly 和 Features 使用，BizFoundation 不依赖它。Playground 是该包的独立消费者，其导航、主题偏好和演示状态不进入基础包。

当前 Playground 没有跨 Feature 业务，故不创建空 BizFoundation；产品模板和非 UI 包由对应任务设计后接入。

## 包与配置

- `flutter/pubspec.yaml` 使用 Pub workspace；解析成功后在工作区保留统一锁文件。
- 每个包声明其直接依赖，禁止假定应用必然安装某个传递依赖。
- 共享包不得引用本机绝对路径或业务项目的源码。
- 应用配置和控制器生命周期由 Assembly / Feature 持有，基础组件不持久化全局单例。
- SDK 与独立 Material 包版本在接入时明确核实；不能用预发布或浮动版本绕过兼容问题。
