# ② Features 层

一个子目录 = 一个业务域，页面、页面状态与本域操作内聚；不直接访问其他 Feature 内部页面或状态，跨域由 App 编排。

源码编入 App target，不单独建 SPM target（需要时再拆）。

## 设置页（强制）

`Settings/` 保持**单页 List**，极简：

- 语言 / 外观必须用 `LanguagePickerView` / `ThemePickerView` 嵌在本页，**禁止** `NavigationLink` 进子页。
- 有付费：解锁入口 + `#if DEBUG`「调试解锁」绑 `LifetimeStore.debugUnlockAll`。Release 无此开关。
- 关于：版本 / 隐私 / 意见反馈 / 给个好评。反馈用 `mailto:` 拉起系统邮箱（收件箱 `AppConfig.feedbackEmail`）。好评走系统评价框（`requestReview`）；第 3 次进根页也会请评。不要用 `requestReview()` 当唯一保底——系统有次数上限。上架后填 `AppConfig.appStoreID`。
- 免费产品：删 `Features/Paywall/`、设置里解锁 Section、以及 `App` 里的 `LifetimeStore` 注入。

## 新增功能

```
Features/
  Settings/          # 已有示例
  Paywall/           # 终身买断墙；文案改 xcstrings
  MyFeature/         # 新建
    MyFeatureView.swift
```

1. 建目录 `Features/<Name>/`
2. UI / 功能编排放这里
3. 可测业务规则 → `packages/__APP_NAME__Core/Sources/BizFoundation/`；业务定制 UI → `ios/BusinessUI/`（同属②）
4. 在 `App/RootView` 挂入口
