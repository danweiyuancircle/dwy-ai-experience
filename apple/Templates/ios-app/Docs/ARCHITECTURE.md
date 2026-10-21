# 四层目录架构（必须遵守）

工程根目录**并列**四层（对齐 TVRemote）：

```
App/              ① APP 层 — 入口、根路由、Info.plist、打包配置
Features/         ② Features 层 — 按子功能分包
BizFoundation/    ③ 业务基础层 — 领域纯逻辑 SPM
Foundation/       ④ 业务无关基础层 — 层锚点；kits 来自统一私有包版本
```

完整真源：`https://github.com/danweiyuancircle/dwy-ai-experience/blob/0.4.1/apple/Docs/ARCHITECTURE.md`

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

- iOS **17.0+**
- `BizFoundation` 无 SwiftUI / StoreKit / PurchaseCore
- 语言 / 外观本页下拉；有付费则 DEBUG 解锁
