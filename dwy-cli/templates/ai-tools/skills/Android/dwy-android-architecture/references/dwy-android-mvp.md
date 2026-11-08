---
description: Android 用 MVP 做页面分工；实际架构读当前项目上下文；业务 Base 落在 BizFoundation；简单静态页和确认框允许无 Presenter
paths:
  - "**/*.java"
  - "**/*.kt"
  - "**/AndroidManifest.xml"
  - "**/res/**/*.xml"
---

# Android MVP 与业务 Base

**实际 MVP 架构以当前项目上下文为准。** 本文件只定大行为，不定骨架、类名、目录、库。

写任何页面前必须先读本仓，再动手。读到的继承链、Contract 切法、基类名字、生命周期挂法、包怎么放，全部跟项目。禁止用记忆里的「标准 MVP」覆盖本仓。

模块四层见 `dwy-android-layering`；注释 / 命名 / AppCompat 见 `dwy-android-core`。Support 与 AndroidX 也跟当前项目推断。

---

## 一、写页面前读什么

打开工程后搜并读（命中即按它写）：

- 已有 `*Presenter` / `*View` / `*Contract` / Presenter 基类
- 业务 `BaseActivity` / `BaseFragment` / `BaseDialog` 的位置与继承链
- 一页的类怎么摆：同功能包，还是本仓已经横切
- View 与 Presenter 怎么绑生命周期（attach / 构造传入 / 其它）

新页对齐读到的那套。禁止另起一套。存量不回溯。

新仓还没有任何页面：用下面行为准则写第一页；之后新页对齐第一页，仍不从外部套模板。

---

## 二、行为准则（骨架仍跟项目）

1. **View 管 UI，Presenter（或本仓对等角色）管业务与请求，数据层管读写。** 有业务的页：请求、校验、状态编排不进 Activity。
2. **Presenter 不碰控件。** 不 `findViewById`，不把 Activity / 控件当字段；需要 Context 走 View 回调。页面销毁后不再调 View。怎么 detach 跟项目。
3. **简单静态页、确认框、单按钮提示：允许不写 Presenter。** 不造空文件。复杂 Dialog 仍走本仓 MVP。
4. **业务 Base 给业务扩展。** `BaseActivity` / `BaseFragment` / `BaseDialog` 落在 BizFoundation（未拆四层则本仓已有的 base 包）：本产品壳。Feature 有 Base 之后禁止直接继承框架页。Foundation 不放本产品页面基类。Base 禁止上帝类。

---

## 三、检查清单

| 检查项 | 严重 |
|---|---|
| 没读本仓已有 MVP / Base 就按外部模板开写 | 高 |
| 新页没对齐本仓已有切法 / 命名 / 库 | 高 |
| 有请求的页在 Activity 里写接口 / 拼业务 | 高 |
| Presenter（或对等角色）持有控件 / Activity，销毁后仍回调 View | 高 |
| 已有业务 Base，新页仍直接继承框架页 | 高 |
| 业务 Base 里出现某 Feature 方法（上帝类） | 高 |
| Foundation 里放本产品 BaseActivity | 高 |
| 静态页 / 确认框硬造空 Presenter | 中 |
