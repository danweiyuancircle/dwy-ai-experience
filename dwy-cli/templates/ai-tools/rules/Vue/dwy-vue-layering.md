---
description: Vue 四层分包与依赖方向（Assembly / Features / BizFoundation / Foundation）；pnpm catalog 根锁定第三方版本
paths:
  - "**/*.vue"
  - "**/*.ts"
  - "**/package.json"
  - "**/pnpm-workspace.yaml"
---

# Vue 四层架构与依赖

适用于 pnpm workspace 的 Vue 3 应用。组件 / 路由 / Pinia 写法见 `dwy-vue-core` / `dwy-vue-pinia`。本文件只管**层、引用边、版本写在哪**。

单壳项目**不建** PlatformFoundation。

---

## 一、层名（冻结）

正式层名只有下表四个。目录 / 包可以叫 `apps/web`、`packages/biz-foundation`，文档可写「本仓包名 X = Foundation」。**禁止**把 `Domain` / `infra` / `core` 当层名。

| 层 | 判定（只用这一条） | 禁止 |
|---|---|---|
| **Foundation** | 换一个完全不同的产品仍原样拿走 | 出现本业务名词 |
| **BizFoundation** | 本产品才有，但跨多个 Feature 都要用 | 页面、导航、某一端壳状态 |
| **Features** | 可整包删/裁剪的业务域 | 被其他 Feature 直接引用 |
| **Assembly** | 生命周期、DI、路由挂载、把实现插进 Protocol | 业务规则、业务计算 |

升层：第二个 Feature 或第二个产品**真在用**，才升到 BizFoundation / Foundation。禁止「可能复用」提前抽。

业务内聚：一个业务域 = `packages/features/` 下的一个包。域内 `api.ts` / `store.ts` / `types.ts` / `route.ts` / `views/` 聚在一起。禁止全局 `views/` `stores/` `api/`。

项目专用、绝不跨项目的页面可放 `apps/web/src/features/`，**依赖边与 `packages/features/*` 相同**：禁止互引、禁止 import `packages/foundation`。

---

## 二、依赖边（强制）

```
apps/web → packages/features/* → packages/biz-foundation → packages/foundation
                  ✕ 互引
```

| 谁 | 允许依赖 | 禁止 |
|---|---|---|
| `apps/web` | `features/*`、`biz-foundation`、`foundation`（仅装配 http 单例） | 业务计算写在壳里 |
| `@acme/orders` | 仅 `@acme/biz-foundation` + catalog 第三方 | `@acme/inventory`、`@/` 宿主路径、`@acme/foundation` |
| `@acme/biz-foundation` | 仅 `@acme/foundation` | `apps/web`、任何 Feature |
| `@acme/foundation` | catalog 第三方 | 任何业务包、Vue Router 业务路由 |

**Feature 互引为零。** 跨域只许三种：升到 `biz-foundation`；Feature 导出工厂 / Options，由 `apps/web` 注入回调；壳编排两个页面。

可复用 Feature **禁止** `import { useXxxStore } from '@/stores/...'`。宿主 store 由 `apps/web` 经 Options 传入。

```ts
// 合法：packages/features/orders 只认端口，不 import inventory
export interface StockPort {
  /** 扣库存。实现由 apps/web 注入。 */
  deduct(sku: string, qty: number): Promise<void>
}
```

```ts
// 禁止
import { useInventoryStore } from '@acme/inventory'  // Feature → Feature
import { useAuthStore } from '@/stores/auth'         // 可复用 Feature → 宿主
import { http } from '@acme/foundation'              // 越层；经 biz-foundation 门面
```

---

## 三、分包树

打开仓库必须能数出四层。业务词只出现在 `packages/features/`（或壳内 `apps/web/src/features/`）。

```
apps/
  web/                            # Assembly
    src/
      main.ts
      router.ts
      stores/                     # 宿主 session，不放业务规则
packages/
  features/                       # Features
    orders/
      package.json
      src/
        api.ts
        store.ts
        types.ts
        route.ts
        views/
    inventory/
  biz-foundation/                 # BizFoundation
    src/
      auth/                       # 内容：跨 Feature 鉴权，不是一层
      protocols.ts
  foundation/                     # Foundation
    src/
      http.ts
      format.ts
pnpm-workspace.yaml               # catalog 只在这
pnpm-lock.yaml
```

禁止把 `orders`、鉴权、http 工厂平铺在 `packages/` 根上，否则层不可见。

```yaml
# pnpm-workspace.yaml
packages:
  - apps/*
  - packages/features/*
  - packages/biz-foundation
  - packages/foundation
```

---

## 四、Monorepo 版本（强制）

第三方版本号**只**出现在 `pnpm-workspace.yaml` 的 `catalog`。子包用 `"catalog:"`。内部包 `"workspace:*"`。选哪个版本走 `dwy-dependency-freshness`。

```yaml
# pnpm-workspace.yaml
catalog:
  vue: 3.5.13
  axios: 1.7.9
```

```json
{
  "name": "@acme/orders",
  "dependencies": {
    "vue": "catalog:",
    "@acme/biz-foundation": "workspace:*"
  }
}
```

禁止子包 `"vue": "^3.5.13"`。禁止每个 Feature 各自锁 axios 版本。

---

## 五、检查清单

| 检查项 | 严重 |
|---|---|
| `packages/` 根平铺业务包，看不出 `features` / `biz-foundation` / `foundation` | 高 |
| Feature `package.json` 依赖另一 Feature | 高 |
| 可复用 Feature import `@/stores/*` | 高 |
| Feature 直接依赖 `@acme/foundation` | 高 |
| 子包写死第三方版本（不用 `catalog:`） | 高 |
| `Domain` / `infra` / `core` 当层名 | 中 |
