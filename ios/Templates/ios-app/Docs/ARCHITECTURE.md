# 四层目录架构（必须遵守）

工程根目录**并列**四层（对齐 TVRemote）：

```
App/              ① APP 层 — 入口、根路由、Info.plist、打包配置
Features/         ② Features 层 — 按子功能分包
BizFoundation/    ③ 业务基础层 — 领域纯逻辑 SPM
Foundation/       ④ 业务无关基础层 — 层锚点；kits 来自统一私有包版本
```

基础库锁定版本见 `Package.swift` 与 `project.yml`，两处必须一致。对应版本规约位于基础库的 `ios/Docs/ARCHITECTURE.md`；源码、公开 API 与示例必须按锁定标签读取。

## 依赖

```
App / Features → BizFoundation → Foundation(kits)
App / Features → Foundation(kits) 直接使用日志/主题/多语言
禁止：BizFoundation → SwiftUI / Features / StoreKit / PurchaseCore
```

## 扩功能

| 事 | 目录 |
|----|------|
| 新页面 | `Features/<Name>/` |
| 可测规则 | `BizFoundation/` |
| 通用基建 | 改骨架仓（④） |
| 终身买断 | App 持有 `LifetimeStore`；限额 / 试用纯函数留 ③ |

## 底线

- iOS **18.0+**
- `BizFoundation` 无 SwiftUI / StoreKit / PurchaseCore
- 语言 / 外观本页下拉；有付费则 DEBUG 解锁

## UI 基础组件与业务组合

- App/Features 统一消费 `DesignKitIOS`；根 scene 注入 `EControlTheme`，用户外观偏好仍归 `ThemeManager`。
- 基础库已有的通用组件必须复用；项目可在 `BusinessUI/` 组合本产品的展示关系，通过值、Binding 和动作回调接入，不读取业务单例或替页面执行任务。出现实际跨 Feature 复用时再建立该目录，不提前建空模块。
- iOS 18 与 iOS 26 通用样式差异由基础库内部适配；项目通过 `eControlPlacement` 表达浮动/内容层级，不复制玻璃版本分支。
- 业务专用图形确需独立材质时，在项目文档记录具体文件、理由和验证范围，再调整对应边界测试；不得以宽泛目录豁免重复的通用控件实现。空模板没有此类例外。
- NavigationLink、导航、系统 toolbar/alert、菜单项和认证品牌控件继续使用原生契约，不能机械禁止所有系统 Button。
- 从项目根执行 `python3 -m unittest discover -s Tests -p 'test_*.py'`，检查平台依赖、锁定版本、主题入口和页面材质越界；仍须编译及目标系统交互验收。
