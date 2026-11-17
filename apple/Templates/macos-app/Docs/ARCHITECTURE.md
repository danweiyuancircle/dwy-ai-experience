# macOS 四层边界

产品统一规范见 [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)。本端内部仍为① App、② Features、③ BizFoundation、④ Foundation 四层；macos/BusinessUI 属于②，本端产品平台适配属于③，不新增层级。

| 需求 | 产品根相对路径 |
| --- | --- |
| 装配、路由、window 生命周期 | macos/App |
| 业务域页面与页面状态 | macos/Features/<Name> |
| 业务定制 UI | macos/BusinessUI |
| UI 无关共享规则与协议 | packages/__APP_NAME__Core/Sources/BizFoundation |
| macOS 业务平台适配 | 按需 macos/Platform |
| 通用基础能力与 UI | AppleAppKit 公开产品 |

- 最低 macOS26，仅 Apple Silicon arm64。本端工程、测试与实际产物的系统/架构基线保持一致。
- App/Features 直接使用满足需求的 DesignKitMac，禁止逐个再套同功能包装或复制通用样式。
- 有业务语义、产品样式或交互组合时，在 BusinessUI 封装；缺口可用 SwiftUI/AppKit 自行实现并内聚，不散写页面，不放入共享逻辑包，不强制先补共享库。
- 共享规则通过产品核心包引用，不将 ios 或产品核心源码加入本端 sources。平台业务实现不独立建包时显式加入 macos/project.yml 的 sources；建包时由 macos/Package.swift 定义 target，只通过 product 引入。
- 通过值、Binding 与动作回调连接业务；App 注入平台实现并持有生命周期，文件授权、危险操作、任务取消、权益与持久化不随 UI 展示迁移。
- 通用主题与共享组件的系统适配归基础库；自行实现部分由项目验证系统适配、键鼠、焦点、窗口与可访问性。原生菜单、文件选择、窗口和认证品牌契约保留。
- 产品根运行 `python3 scripts/check-architecture.py`，进入 macos 运行 XcodeGen 后构建；静态检查、签名和启动不能代替实际窗口交互与视觉验收。
