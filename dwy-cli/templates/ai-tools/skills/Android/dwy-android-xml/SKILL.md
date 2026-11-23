---
name: dwy-android-xml
description: 编写、修改、排查或评审 Android XML 布局、字符串、尺寸、图片、样式和主题资源时使用，适用于 Android Support 与 AndroidX 的 Views 页面和共用资源。
---

# Android XML 资源与布局

- 先确认目标模块、变体、宿主主题和实际加载的资源。修改已有资源 ID、名称或类型前，核对代码引用、布局覆写、主题和资源限定符，保留调用方需要的资源契约。
- 沿用项目的资源命名与目录约定。新增布局按用途命名，例如 `fragment_home.xml` 或 `item_channel.xml`。可见文案和有意义的图标描述使用字符串资源，翻译和屏幕尺寸差异通过资源限定符处理，保留默认资源。
- 宽高、间距等设计尺寸使用 `@dimen`，资源值采用 `dp`，字号资源采用 `sp`。颜色、背景和控件样式优先复用现有主题与资源，验证夜间模式、系统字体缩放和布局适配。对作用依赖其他布局或代码的属性，说明这项约束。
- 在已有 Support 或 AndroidX 页面中，控件全限定名、`android:` 与 `app:` 属性、样式父级、绑定 ID 都要与实际依赖及主题相符。沿用页面的绑定方案与设计体系。调整控件时检查其测量、状态样式、点击及焦点行为。
- TV 页面用现有焦点策略，必要时设置 `nextFocus*`。调整结构后用方向键验证默认焦点、跨区域移动和返回后的焦点恢复。使用项目 Gradle Wrapper 编译相关变体，并在目标系统检查实际渲染和交互。

按需查阅 [Android 资源与限定符](https://developer.android.com/guide/topics/resources/providing-resources) 和 [Android TV 导航](https://developer.android.com/training/tv/get-started/navigation)。
