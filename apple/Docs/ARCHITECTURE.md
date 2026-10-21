# 四层目录架构规约（强制）

与 TVRemote 一致：**工程根下并列四个目录**，一眼能分清层级。

部署：iOS **17.0+** · macOS **14.0+** · Swift **6.0**。

---

## 1. 目录即分层

```
<工程根>/
  App/                 ① APP 层
  Features/            ② Features 层
  BizFoundation/       ③ 业务基础层
  Foundation/          ④ 业务无关基础层
  Resources/           资源（属 ① 打包，与 TVRemote 资源位置同类）
  Package.swift        定义 ③，依赖 ④
  project.yml          ① 打包真源
  Docs/ARCHITECTURE.md
```

| 目录 | 层 | 职责 |
|------|-----|------|
| **App/** | ① | `@main`、根路由、Info.plist、全局注入；打包相关配置在 `project.yml` |
| **Features/** | ② | 按子功能分包 UI（`Features/<Name>/`） |
| **BizFoundation/** | ③ | 领域纯逻辑 SPM product；可 `swift test` |
| **Foundation/** | ④ | 层锚点 + 说明；**kits 实现在骨架仓**，本工程 git 版本依赖 |

对照 TVRemote：

| 本模板 | TVRemote |
|--------|----------|
| `App/` | `TVRemote/App/` |
| `Features/` | `TVRemote/Features/` |
| `BizFoundation/` | `Sources/BizFoundation/` |
| `Foundation/` | `Sources/Foundation/` |

模板把四层提到**工程根并列**，避免再套一层产品名目录导致结构含糊。

---

## 2. 依赖

```
App / Features ──► BizFoundation ──► Foundation kits（CoreKit / LogKit / …）
App / Features ──► Foundation kits（直接用主题、多语言、日志）

禁止：
  Foundation kits ↛ BizFoundation / Features / App
  BizFoundation ↛ SwiftUI / Features / App
```

③ 仅可依赖：`CoreKit`、`L10nKit`、`LogKit`、`CacheKit`。
③ 禁止：`DesignCore`、`DesignKitIOS` / `DesignKitMac`、`PurchaseCore`、StoreKit、SwiftUI、UIKit、AppKit。

---

## 3. ④ Foundation 与骨架仓

- **目录 `Foundation/`** 必须存在，保证四层在树上可见。
- **源码**维护在骨架仓 `apple/Sources/Shared` + `apple/Sources/iOS|macOS`；认证源码位于 `modules/auth/apple/Sources`。
- 业务仓 `Package.swift` / `project.yml` 用 `dwy-ai-experience` 的 **git tag**（`from:` + `Package.resolved`），**禁止** `path:` 指本地 `ios-arc`。不要把 LogKit 等复制进业务仓。
- `Foundation/README.md` 列出本 App 使用的 product。

---

## 4. 扩展

| 需求 | 落点 |
|------|------|
| 打包 / 版本 / 签名 | `project.yml` + `App/Info.plist` |
| 新功能 UI | `Features/<Name>/` |
| 可测业务规则 | `BizFoundation/` |
| 日志 / 多语言引擎 / 通用主题桥 / 终身买断 | 骨架仓（④） |

---

## 5. 自检

- [ ] 根下存在 `App` `Features` `BizFoundation` `Foundation` 四个目录
- [ ] `BizFoundation` 无 SwiftUI / StoreKit / PurchaseCore
- [ ] 未 vendoring 一份 Foundation 源码
- [ ] 新 Feature 使用独立子目录
- [ ] 语言 / 外观是设置本页下拉，不是子页
- [ ] 有付费则 `LifetimeStore` + `#if DEBUG` 解锁开关
