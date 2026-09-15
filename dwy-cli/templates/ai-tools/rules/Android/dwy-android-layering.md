---
description: Android 四层模块与依赖方向（app / features / biz-foundation / foundation）；Gradle Version Catalog 根锁定第三方版本
paths:
  - "**/*.kt"
  - "**/*.java"
  - "**/*.gradle"
  - "**/*.kts"
  - "**/libs.versions.toml"
  - "**/settings.gradle"
---

# Android 四层架构与依赖

适用于多模块 Android 应用。注释 / 命名 / AppCompat 见 `dwy-android-core`。本文件只管**Gradle 模块层、引用边、版本写在哪**。模块**内部** Java 包仍按功能聚合（见 `dwy-android-core`「包组织」）。

新项目强制本结构。未拆模块的存量**不回溯拆包**；新增模块必须按本文件落层。Support 老项目另走 `dwy-android-support-only`。

单壳项目**不建** PlatformFoundation。

---

## 一、层名（冻结）

正式层名只有下表四个。模块可以叫 `:app`、`:biz-foundation`，文档可写「本仓 `:layer-infra` = Foundation」。**禁止**把 `Domain` / `infra` / `core` 当层名。

| 层 | 判定（只用这一条） | 禁止 |
|---|---|---|
| **Foundation** | 换一个完全不同的产品仍原样拿走 | 出现本业务名词 |
| **BizFoundation** | 本产品才有，但跨多个 Feature 都要用 | 页面、导航、某一端壳状态 |
| **Features** | 可整包删/裁剪的业务域 | 被其他 Feature 直接引用 |
| **Assembly** | 生命周期、DI、路由挂载、把实现插进 Protocol | 业务规则、业务计算 |

升层：第二个 Feature 或第二个产品**真在用**，才升到 BizFoundation / Foundation。禁止「可能复用」提前抽。

业务内聚：一个业务域 = `:features:<name>`。域内 Activity / ViewModel / Repository 聚在该模块。禁止全局 `activities/` 模块。

---

## 二、依赖边（强制）

```
:app → :features:* → :biz-foundation → :foundation
            ✕ 互引
```

| 谁 | 允许 project 依赖 | 禁止 |
|---|---|---|
| `:app` | `:features:*`、`:biz-foundation` | 业务规则写在 Application / HomePresenter |
| `:features:orders` | **仅** `implementation project(':biz-foundation')` | 其它 Feature、`:foundation`、`:app` |
| `:biz-foundation` | `:foundation`（可用 `api` 给编译用，见下） | Feature / app |
| `:foundation` | 无 project 下层 | 业务模型、Feature |

**Feature 互引为零。** 跳转只走 `:app`。跨域只许：升到 `:biz-foundation`；Feature 依赖 `biz-foundation` 里的接口，由 app 注入；壳编排。

**透传不等于可直连。** `:biz-foundation` 即使 `api project(':foundation')`，Feature **源码仍禁止** `import` foundation 包名。要用 Http/Log，走 biz-foundation 门面。

```gradle
// features/orders/build.gradle
dependencies {
    implementation project(':biz-foundation')
    implementation libs.okhttp
}
```

```gradle
// 禁止
implementation project(':features:inventory')
implementation project(':foundation')
implementation project(':app')
```

---

## 三、分包树

打开工程必须能数出四层。业务词只出现在 `features/` 下。

```
:app                              # Assembly
:features:orders                  # Features
:features:inventory
:biz-foundation                   # BizFoundation（鉴权、跨域协议放这个模块里面）
:foundation                       # Foundation（Http / Log / 进程工具）
```

```
app/
features/
  orders/
  inventory/
biz-foundation/
  src/main/java/.../bizfoundation/auth/
foundation/
  src/main/java/.../foundation/http/
gradle/libs.versions.toml
settings.gradle
```

`settings.gradle` include 上述模块。鉴权不是独立层，是 `:biz-foundation` 内的包。

---

## 四、Monorepo 版本（强制）

第三方版本号**只**出现在 `gradle/libs.versions.toml`。模块用 `libs.xxx`。内部模块 `project(':x')`。选哪个版本走 `dwy-dependency-freshness`。

存量若仍用根 `config.gradle` 的 `ext`，视为同一 catalog，禁止再在子模块写版本。

```toml
# gradle/libs.versions.toml
[versions]
okhttp = "4.12.0"

[libraries]
okhttp = { module = "com.squareup.okhttp3:okhttp", version.ref = "okhttp" }
```

```gradle
// features/orders/build.gradle
dependencies {
    implementation project(':biz-foundation')
    implementation libs.okhttp
}
```

禁止 feature 模块 `implementation 'com.squareup.okhttp3:okhttp:4.12.0'`。

---

## 五、检查清单

| 检查项 | 严重 |
|---|---|
| 无 `:features` / `:biz-foundation` / `:foundation` 三层模块（新项目） | 高 |
| Feature `implementation` 另一 Feature 或 `:foundation` 或 `:app` | 高 |
| Feature 源码 `import` foundation 包名（即使经 `api` 透传） | 高 |
| 开机链 / 业务编排写在 `:app` 的 Presenter | 高 |
| 子模块写死第三方坐标版本 | 高 |
| `Domain` / `infra` / `core` 当层名 | 中 |
