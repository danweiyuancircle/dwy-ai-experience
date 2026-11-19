# 产品 UI 规范：来源与取舍

核对日期：2026-11-17。本文件供维护、溯源和再次研究使用；普通页面开发执行 SKILL.md 与按上下文选择的分端资料。下文是对公开原则的中文归纳及跨平台取舍，不是上游完整规则的复制或逐条翻译，也不要求安装这些项目。

## 来源

| 项目 | 核对版本与许可证 | 提炼到本 Skill 的内容 |
|---|---|---|
| [Impeccable](https://github.com/pbakaus/impeccable) | `d41d9860b0094dcb68030657da63461212835aaa`；Apache-2.0 | 页面模式区分、操作型界面的熟悉感与一致性、删减冗余、清晰文案、完整状态 |
| [UI Skills / baseline-ui](https://github.com/ibelick/ui-skills) | `65cc0edb4f64fe8bfe7e9c59466074de25bece76`；MIT | 优先已有组件、减少装饰、复用 token、图标命名、空状态下一步、克制动效 |
| [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) | `434b7f91364665f2f733b310ec54809bf8f37937`；MIT | 焦点与键盘、表单与反馈、状态导航、长内容、布局稳定、适配与动态效果偏好 |
| [Radix Primitives](https://github.com/radix-ui/primitives) | `eb3a2b7091293e27df8f9ba906632d8daa3d81a3`；MIT | 将复杂交互交给成熟组件；视觉可定制，语义、焦点与键盘行为仍需完整 |
| [Anthropic / frontend-design](https://github.com/anthropics/skills/tree/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/frontend-design) | `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`；该 Skill 为 Apache-2.0 | 从用户任务和真实内容形成设计意图，避免无视场景的模板；明确需求优先，文案服务理解与使用 |
| [Expo / expo-native-ui、expo-design-system](https://github.com/expo/skills) | `dfdebcc6c4c1bf7a9471cefd6b6f39c7ba6c884d`；MIT | 沿用既有主题与平台控件，处理键盘、草稿、返回和完整数据状态；将原生界面与网页习惯区分 |

以上仓库在核对时均公开、未归档。版本号用于定位本次研究，不是消费项目的依赖版本要求；许可证以对应上游版本为准。研究只读取公开仓库与官方资料，没有安装包、执行远程脚本或上传项目代码。

### 直接资料

- Impeccable：[入口与页面模式](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/.agents/skills/impeccable/SKILL.md)、[操作型页面](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/.agents/skills/impeccable/reference/operate.md)、[distill](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/.agents/skills/impeccable/reference/distill.md)、[clarify](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/.agents/skills/impeccable/reference/clarify.md)、[LICENSE](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/LICENSE)。
- UI Skills：[baseline-ui](https://github.com/ibelick/ui-skills/blob/65cc0edb4f64fe8bfe7e9c59466074de25bece76/skills/baseline-ui/SKILL.md)、[LICENSE](https://github.com/ibelick/ui-skills/blob/65cc0edb4f64fe8bfe7e9c59466074de25bece76/LICENSE)。
- Vercel：[界面规范](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/AGENTS.md)、[LICENSE](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/LICENSE)。
- Radix：[组件介绍](https://www.radix-ui.com/primitives/docs/overview/introduction)、[无障碍职责](https://www.radix-ui.com/primitives/docs/overview/accessibility)、[源码与版本](https://github.com/radix-ui/primitives/tree/eb3a2b7091293e27df8f9ba906632d8daa3d81a3)、[LICENSE](https://github.com/radix-ui/primitives/blob/eb3a2b7091293e27df8f9ba906632d8daa3d81a3/LICENSE)。官方文档是核对日期的在线内容，不声称与源码快照逐字对应。
- Anthropic：[frontend-design](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/frontend-design/SKILL.md)、[该 Skill 的许可证](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/frontend-design/LICENSE.txt)。
- Expo：[原生界面](https://github.com/expo/skills/blob/dfdebcc6c4c1bf7a9471cefd6b6f39c7ba6c884d/plugins/expo/skills/expo-native-ui/SKILL.md)、[设计系统](https://github.com/expo/skills/blob/dfdebcc6c4c1bf7a9471cefd6b6f39c7ba6c884d/plugins/expo/skills/expo-design-system/SKILL.md)。
- Impeccable 的分端补充：[原生适配](https://github.com/pbakaus/impeccable/blob/d41d9860b0094dcb68030657da63461212835aaa/.agents/skills/impeccable/reference/adapt.native.md)。

## 分端差异的官方核对资料

Skills 提供方法，平台官方资料用于校准适用边界；不将第三方 Skill 的偏好当成所有系统的标准。以下在线资料均按核对日期读取，没有可统一锁定的发布版本。

| 资料 | 用于核对的差异 |
|---|---|
| Apple HIG：[布局](https://developer.apple.com/design/human-interface-guidelines/layout)、[窗口](https://developer.apple.com/design/human-interface-guidelines/windows)、[键盘](https://developer.apple.com/design/human-interface-guidelines/keyboards)、[无障碍](https://developer.apple.com/design/human-interface-guidelines/accessibility) | 可用窗口、安全区、文字放大、系统窗口与键盘约定；平板不能仅因有键盘就变成桌面应用 |
| Android：[移动布局](https://developer.android.com/design/ui/mobile/guides/layout-and-content/layout-basics)、[窗口 Insets](https://developer.android.com/develop/ui/compose/layouts/insets)、[预测性返回](https://developer.android.com/design/ui/mobile/guides/patterns/predictive-back) | 系统栏和键盘遮挡、实际尺寸与姿态、原生返回行为；不将 iOS 控件和导航直接移植 |
| Microsoft：[键盘交互](https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions) | Windows 的焦点、快捷键与输入约定；不照搬其他桌面系统的按键规则 |
| MDN：[Visual Viewport](https://developer.mozilla.org/en-US/docs/Web/API/Visual_Viewport_API)；WAI-ARIA APG：[模态对话框](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | 手机浏览器键盘与可见视口、网页模态焦点；原生客户端的窗口或导航规范不能代替浏览器行为 |

Apple HIG 的正文通过其公开文档 JSON 数据核对；网页壳仅返回标题不视为已读正文。具体实现所用 API、SDK 和系统版本仍在实际开发时按项目核实，本 Skill 不锁定易变的实现写法。

## 取舍依据

这些来源提供的是不同层次的能力：Impeccable、UI Skills 和 Anthropic 提供设计指导，Expo 提供特定生态的原生开发规则，Vercel 是 Web 实践规范，Radix 是组件库。提取交集后按运行环境拆分，实际实现仍使用项目已有工具；组件库本身不会决定业务信息层级或保证产品质感。

| 上游存在的偏好或技术细节 | 本 Skill 的取舍 |
|---|---|
| Tailwind、React、特定动画包、CSS 工具类 | 保留复用组件与 token 的原则，不要求跨栈安装或换框架 |
| 全面禁止渐变、紫色或某类装饰 | 操作型页面不无故添加；品牌要求与营销、展示任务独立判断 |
| 固定动画时长、只允许特定动画属性 | 优先平台与现有高效动效，不拖延操作；表现性需求按实际性能验证 |
| 卡片禁令、固定圆角或颜色数量 | 依据对象与分组决定容器，维持项目一致性，不套统一数值 |
| 固定行数后虚拟化、统一请求耗时目标 | 按实际数据规模与性能测量决定，避免无证据加复杂度 |
| 自动乐观更新或机械去掉确认步骤 | 保留业务语义、真实错误与数据安全；仅在可正确撤销或协调状态时采用 |
| Web 专属焦点、路由、视口与安全区写法 | 核心描述目标，具体实现遵循 Web、Apple、Android 等平台规范 |
| 要求所有项目大胆创新、生成鲜明视觉世界 | 新建或明确重设计时围绕真实品牌判断；成熟工具页局部修改优先一致性 |
| Expo 包、目录、开发工具和具体版本要求 | 只吸收平台适配、复用主题、真实操作与状态原则，不带入其他技术栈 |
| 将平台、设备和渲染方式视为同一分类 | 按上下文组合规则：手机网页是网页加移动场景，桌面网页容器分清内容与宿主 |

## 再次维护时

先定位实际出现的页面问题，再判断是规则缺口、Skill 未加载还是执行未遵守；不要每次看到装饰就新增一条全局禁令。更新上游来源时检查规则是否仍适用于现有平台，不自动追最新依赖、不改用户已确认的视觉方向。
