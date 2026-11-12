# macOS 26 通用控件抽取计划

目标：从 ADBox 已有控件提炼可独立消费的 DesignKitMac，后续 macOS 应用直接使用。用户已确认采用现有自有基础库、macOS 26.0，无须旧版系统兼容。

2026-11-12 范围更新：用户改为先基于 ADBox 双端分析，iOS 与 Mac 各自一份规范及组件。后续以 `ios/Docs/DESIGN_SYSTEMS.md`、`ios/Docs/IOS_DESIGN_SYSTEM.md`、`ios/Docs/MACOS_DESIGN_SYSTEM.md` 为设计依据。本计划已生成的 Mac 原型保留；暂停扩大迁移，不标为稳定发布或 ADBox 已接入。

架构：保留原生 Button/Menu/Picker/TextField/Toggle 语义；主题、布局和材质集中维护。组件不依赖 ADBox 的 Palette、Pro、设备及日志历史。DesignCore 与 iOS 接口不变。

技术：Swift 6、SwiftUI、AppKit；不新增外部依赖。基线改动同步根包、Mac 模板与支持文档；iOS 版本不提高。

范围：按钮及图标按钮、动作菜单、单选/分段选择、文本框、开关、表单行、可输入下拉建议、操作组；独立示例和测试。ADBox 的原有调用在组件发布前不指向尚未发布 revision，不提交本机依赖路径。

- [ ] 测试先覆盖下拉过滤/去重/键盘导航/候选更新、独立组件布局和原生控件绑定。
- [ ] DesignKitMac 实现主题、原生控件封装与通用组合，抽取可输入下拉的展示交互，历史持久化留业务。
- [ ] 创建独立消费示例，涵盖明暗、各控件状态、图标与资源标签、长文案和校验提示。
- [ ] 同步 macOS 26 平台与模板，说明公开 API、ADBox 对应迁移位置及版本接入方式。
- [ ] 定向测试、组件/示例构建、实际启动交互；核对 diff 和依赖锁文件。

风险与验证：macOS 26 专用 API 不以更高系统 API 替代；焦点和减少动态效果按原生语义保留；下拉不重写中文组合输入。公共库升级需要消费项目更新固定版本。本机 macOS 27 的运行不能作为 26 实机验收。
