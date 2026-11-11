# macOS 窗口与系统外观

- 使用现有系统窗口、侧栏、工具栏、菜单和焦点行为；验证窗口缩放、最小尺寸、键盘、鼠标、菜单和辅助功能。不要把 iPhone 的固定尺寸布局搬到 Mac。
- macOS 26+ 使用适配 SDK 构建时先检查系统组件的 Liquid Glass；仅在适合的自定义控件使用系统 API，避免叠加遮挡内容。仅当实际项目仍支持 macOS 15 时保留其可用的原生外观，不把普通材质或系统旧样式称为 Liquid Glass API。
- 根据 SDK 和运行时版本判断 API 可用性；检查深浅色、减少透明度、增加对比度和可读性。按任务在目标 macOS 版本启动、操作并观察界面；编译、签名或进程存在不能代替视觉与交互验收。
- 具体行为以 Apple 官方文档及当前 SDK 为准：https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
