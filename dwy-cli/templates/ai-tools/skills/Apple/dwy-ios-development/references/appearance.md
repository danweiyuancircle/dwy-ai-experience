# iOS 系统外观与 Liquid Glass

- iOS 26+ 使用适配 SDK 构建时，先检查系统导航、工具栏、控件和弹层的原生外观；自定义背景可能遮挡系统效果。根据产品设计适配，勿给所有内容叠加玻璃。
- 仅在适合的自定义控件使用系统玻璃 API，检查 SDK 和运行时可用性；iOS 18–25 保留可用、可读的原生或项目既有外观，不将普通透明背景称作 Liquid Glass。
- 在受影响的目标系统检查深浅色、减少透明度、增加对比度、动态字体、触控区域和内容遮挡。记录 SDK、系统、设备及实际交互与视觉验证；只编译或截图空白不能证明通过。
- 具体行为以 Apple 官方文档及当前 SDK 为准：https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
