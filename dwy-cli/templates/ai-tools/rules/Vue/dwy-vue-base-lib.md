---
description: 团队内部基础库强制复用规范（eui UI 组件 + ekit 工具：禁重复造轮子、HTTP/存储/日期/校验/脱敏走 ekit、UI 走 eui）
paths:
  - "**/*.vue"
  - "**/*.ts"
---

# Vue 团队基础库强制复用规范

`dwy-vue-core` rule 的团队内补充。通用 Vue 工程规范见 `dwy-vue-core`；本文件只管「凡 eui / ekit 已提供的能力，禁止自行实现，也禁止引入其他库重复造轮子」。

`@dwydev/eui` 与 `@dwydev/ekit` 是团队内部 npm 基础库，分别覆盖 UI 组件层与通用工具层。

---

## 一、必须复用的能力域

| 能力域 | 归属 |
|--------|------|
| 通用 UI 组件（Button / Input / Select / Dialog / Drawer / Form / Table 等） | eui |
| 主题 / 设计 tokens / 暗色模式 | eui |
| 表单校验（vee-validate + zod 集成） | eui + ekit |
| 中后台 / 落地页设计规范 | eui（references） |
| HTTP 客户端（拦截器 / token / 刷新 / 解包） | ekit |
| 本地存储 / Cookie | ekit（storage / cookie） |
| 日期 / 时间格式化 | ekit（date） |
| 数据校验 schema | ekit（validators） |
| PII 数据脱敏 | ekit（masking） |
| 剪贴板 / 文件下载 / qs 序列化 | ekit |
| VueUse 再导出（debounce / throttle / clickOutside / mediaQuery 等） | ekit（hooks） |

### 查阅方式（关键）

**在编写任何 Vue 代码前，以及调用任何 eui / ekit 提供的 API 之前，必须先用 `Skill` 工具加载对应 skill 查阅当前最新接口。** 本文件只规定约束与边界，**不固化**组件 props、函数签名 —— 这些会随版本演进，固化在 rule 里会与实际包不同步。

```
Skill 工具调用：
  - skill="dwy-eui"   组件库 API 与设计规范
  - skill="dwy-ekit"  工具库 API 与契约
```

---

## 二、强制规则

- **禁止**业务代码出现 `axios` / `fetch` / `new XMLHttpRequest`，HTTP 走 ekit `createRequest`
- **禁止**直接 `localStorage.getItem` / `setItem` / `removeItem`，走 ekit storage / `useStorage`
- **禁止**直接 `document.cookie` 或单独引入 `js-cookie`，走 ekit cookie
- **禁止**业务代码 `new Date()` / `toLocaleString` / 直接 `import dayjs`，走 ekit date
- **禁止**手写 `navigator.clipboard` / `document.addEventListener('click', ...)` 监听，走 ekit copy / hooks
- **禁止**自定义已有 UI 组件（Button / Input / Select / Dialog / Form / Table 等），走 eui
- **禁止**自定义已有日期 / 时间 / 验证 / 脱敏 / 下载 工具函数，走 ekit
- 涉及任一能力域，**先查 skill 拿到当前 API，再写代码**

---

## 三、API 请求

### 强制规则

- HTTP 客户端**必须**用 ekit `createRequest` 创建，全局唯一实例放 `core/http.ts`（具体参数与插件查 `dwy-ekit` skill）
- **禁止**业务代码 `axios.create()` / `fetch()` / `new XMLHttpRequest()`
- 响应解包契约与 dwyeapi 对齐（`{ code, message, data }`），具体类型与守卫查 `dwy-ekit` skill
- 401 / 422 / 业务错误的统一处理由 ekit request 插件完成（具体 API 查 `dwy-ekit` skill）
- 业务侧 catch 用 ekit 提供的 `isApiBusinessError` 类型守卫做分支（`NOT_FOUND` / `VALIDATION_ERROR` / `PERMISSION_DENIED` 等）

> API 函数的目录归属、独立导出、类型标注等结构约定见 `dwy-vue-core` 第六节。

### 示例

```typescript
// core/http.ts —— 全局唯一 HTTP 客户端（具体 plugins 查 dwy-ekit skill）
import { createRequest } from '@dwydev/ekit'

export const request = createRequest({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  plugins: [
    /* tokenPlugin / refreshTokenPlugin / unwrapPlugin —— 具体用法查 dwy-ekit skill */
  ],
})

// modules/users/api.ts —— 该业务的 API
import { request } from '@/core/http'
import type { UserInfo, UserCreate } from './types'

export function getUsers(params: { page: number; page_size: number }) {
  return request.get<{ items: UserInfo[]; total: number }>('/users', { params })
}

export function createUser(data: UserCreate) {
  return request.post<UserInfo>('/users', data)
}
```

---

## 四、通用 hooks 走 ekit

通用 hooks（debounce / throttle / clickOutside / mediaQuery 等）**禁止**自己造，走 ekit hooks（具体 API 查 `dwy-ekit` skill）。

---

## 五、样式覆盖 eui

覆盖 eui 内部样式用 scoped CSS + `:deep(...)`（其余样式规范见 `dwy-vue-core` 第八节，优先 Tailwind）。

---

## 六、错误拦截走 ekit

401 / 422 / 业务错误的拦截走 ekit request 插件（查 `dwy-ekit` skill），**禁止**每个 API 都包 try-catch。业务侧统一在页面级或 store 级处理，用 `isApiBusinessError` 守卫分支。

---

## 七、违规检测清单（基础库相关）

AI 编写或审查 Vue 代码时，涉及 eui / ekit 必须检查以下违规模式（通用框架违规清单见 `dwy-vue-core` 第十四节）：

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 未查 skill | 使用 eui / ekit API 前未先查 `dwy-eui` / `dwy-ekit` skill | 高 |
| ekit 重复造轮子 | 自造 HTTP / storage / cookie / date / 校验 / 脱敏 等 ekit 已提供能力 | 高 |
| eui 重复造轮子 | 自造已有 UI 组件（Button / Input / Dialog 等） | 高 |
| 组件直调 axios | 组件内 `axios.get` / `fetch` / `new XMLHttpRequest` | **致命 → STOP** |
| 直接 localStorage | `localStorage.getItem` / `setItem` 出现在业务代码 | 高 |
| 直接 new Date | `new Date()` / `toLocaleString` / 直接 `import dayjs` | 高 |
| 旧 axios 例子 | 业务里出现 `axios.create()` / `interceptors.request.use(...)` | **致命 → STOP** |
