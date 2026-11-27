# Flutter 状态、生命周期与界面

先读取当前任务匹配的 Flutter 官方 Skill；架构使用 `dwy-flutter-architecture`，语言与异步规范使用 `dwy-dart-development`，不要求为只改 Widget 读取全部入口。

## 响应式状态

- 单向数据流：用户动作进入状态持有者，业务数据经 Repository 更新，再驱动界面。状态管理框架按项目决定。
- 页面状态留在 Feature；应用壳持有依赖图、路由及生命周期。跨 Feature 的业务契约放 BizFoundation，不建万能全局 Store。
- `ChangeNotifier`、`ValueNotifier`、`setState` 和已选框架各有适用范围；不把“不适合某个项目”描述成 Flutter 已废弃。
- 已采用 Riverpod 时，依据当前锁定版本区分生成式与手写 Provider；取消订阅、自动释放、保活策略必须匹配真实生命周期。
- 请求或设备切换时避免旧结果覆盖新状态。取消后仍等待资源清理，不把取消伪装成网络故障或成功。
- Widget 的 build 不发起重复副作用，不创建每次重建都泄漏的控制器、订阅和客户端。持有者负责 dispose/close。

## 统一 UI 与适配

- 已采用 `dwy_design` 时必须使用其已有组件，禁止在页面手写等价实现：

| 禁止在业务页面直接写 | 改用 |
| --- | --- |
| 裸 `CupertinoButton`、自绘按钮、`GestureDetector` 包文字当按钮 | `DwyButton` |
| 裸 `CupertinoTextField`、`CupertinoSearchTextField` | `DwyTextField`、`DwySearchField` |
| 手写设置分组与行 | `DwySettingsGroup`、`DwySettingsTile` |
| 手写空态、加载、错误与重试 | `DwyStatusView` |
| 直接 `showCupertinoDialog` / `showCupertinoModalPopup` 做确认或底部面板 | `showDwyConfirmation`、`showDwySheet` |
| 手写 `CupertinoPageScaffold` + 导航栏做玻璃页面 | `DwyScaffold` |
| 页面里硬编码颜色、间距、圆角 | `DwyTheme.tokensOf(context)` 与主题色 |

  以上以所用版本 `dwy_design` 实际导出为准。导航栏、Tab、日期选择器等从 `dwy_design` 导入官方控件。只有核实组件缺失或确实无法满足需求时，才在 Feature 或应用 UI 层补具体缺口，并优先组合共享组件。
- 通用组件属于 Foundation，产品专属组合留在 Feature。
- 默认中性灰白 + 蓝强调色、系统字体、浅深跟随系统；通过主题令牌及组件主题定制，不在各页面散写另一套颜色和尺寸。
- 基础组件处理禁用、加载、错误、语义标签及足够的点击区域；禁用父组件时检查内部开关和按钮是否仍可触发。
- 用约束和响应式布局处理手机/平板/桌面预览；测试窄屏、大字体、长文案、键盘及安全区域，不写死状态栏/手势区高度。
- 保持双端约定视觉；系统返回、文本选择、键盘、安全区域及权限入口依平台验证。Flutter 风格组件不等于系统原生控件。
- 异步内容区区分首次加载、已有数据刷新、空结果、失败和取消；不伪造进度或连接状态。
