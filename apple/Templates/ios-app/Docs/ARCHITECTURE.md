# iOS 四层边界

产品统一规范见 [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)。本端内部仍为① App、② Features、③ BizFoundation、④ Foundation 四层；ios/BusinessUI 属于②，本端产品平台适配属于③，不新增层级。

| 需求 | 产品根相对路径 |
| --- | --- |
| 装配、路由、scene 生命周期 | ios/App |
| 业务域页面与页面状态 | ios/Features/<Name> |
| 业务定制 UI | ios/BusinessUI |
| UI 无关共享规则与协议 | packages/__APP_NAME__Core/Sources/BizFoundation |
| iOS 业务平台适配 | 按需 ios/Platform |
| 通用基础能力与 UI | AppleAppKit 公开产品 |

- iOS/iPadOS 最低18，project.yml 与共享包平台声明按真实消费者设置。业务核心通过相对 package product 引入，不能将其或 macos 源码加入本端 sources。
- App/Features 直接使用满足需求的 DesignKitIOS，不逐个包装共享控件。根 scene 装配 EControlTheme，用户外观偏好归 ThemeManager。
- BusinessUI 只承载业务语义、产品样式或交互组合，优先组合共享组件；缺口允许用 SwiftUI/UIKit 自行实现并内聚，不散写页面，不放入共享逻辑包，也不强制先补基础库。
- 平台业务实现不独立建包时显式加入 ios/project.yml 的 sources；建包时由 ios/Package.swift 定义 target，只通过 product 引入。App 创建平台实现并按协议注入，生命周期与任务取消归清晰 owner。
- iOS18与26的通用控件和材质差异归基础组件；项目用 eControlPlacement 表达浮动/内容层级，不复制页面玻璃分支。原生导航、toolbar/alert、菜单项和认证品牌控件保留平台契约。
- 业务专用绘制确需材质API时，在本文记录具体文件、缺口和验证范围，并将 BusinessUI 下的具体文件登记到 ios/Tests/test_ui_boundary.py 的 BUSINESS_MATERIAL_SOURCES；不豁免目录、页面或平台依赖。自行实现部分验证系统适配与可访问性。
- 产品根运行 `python3 scripts/check-architecture.py` 与 `python3 -m unittest discover -s ios/Tests -p 'test_*.py'`。前者覆盖结构，后者覆盖产品链接、锁定版本、主题入口与直接材质边界，均不代替 SDK 编译、语义审查或设备验收。
