# ② Features 层

一个子目录 = 一个功能子包（对齐 TVRemote `Features/*`）。

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
3. 可测业务规则 → `BizFoundation/`
4. 在 `App/RootView` 挂入口
