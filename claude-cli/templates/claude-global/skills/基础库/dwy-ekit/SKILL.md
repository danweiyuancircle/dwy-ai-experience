---
name: dwy-ekit
description: "@dwydev/ekit 工具库使用指南。涉及以下任何主题，**必须**使用此 skill（即使用户没有说 'ekit'）：HTTP 请求 / axios 封装 / token 刷新 / dwyeapi 响应契约对接 / localStorage / Cookie / useStorage / useCookie / 日期格式化 / 时区处理 / dayjs / 表单校验 / zod schema / vee-validate / PII 脱敏 / 剪贴板 / useClipboard / 文件下载 / Blob / 查询字符串 / qs / Vue composables（debounce / throttle / click-outside / event-listener / window-size / media-query / intersection-observer / resize-observer / useFormPersist）。本 skill 是 @dwydev/ekit 的唯一权威导航来源，禁止绕过 ekit 直接手写底层 API。"
ekit_baseline_version: "0.8.0"
---

# @dwydev/ekit 工具库使用指南

Vue 3 项目通用工具库。**薄封装层**：底层用 axios / dayjs / zod / js-cookie / qs / file-saver / @vueuse/core，对外**只暴露 ekit 自有契约**，不泄露底层库类型。

10 个模块：`request` / `storage` / `cookie` / `date` / `validators` / `copy` / `qs` / `file` / `hooks` / `masking`。

本 skill 索引基于 ekit **0.8.0**。消费方版本可能不同 — 见 [版本兼容规则](#版本兼容规则)。

---

## 查 API 标准动作（核心：每次写 ekit 代码前都做）

ekit 共 82 个对外导出。**本文档不再镜像函数签名** —— 因为会随版本漂移。需要某个 API 的精确签名时，按下面顺序拿：

### 第一步：定位 ekit 真实版本

读消费方项目 `package.json`，找 `dependencies["@dwydev/ekit"]` 或 `peerDependencies["@dwydev/ekit"]`。这才是写代码的依据。

### 第二步：读 module-manifest.json（一次拿导出索引）

从 ekit 0.8.0 起，npm 包带一份导出清单：

```
<project-root>/node_modules/@dwydev/ekit/dist/module-manifest.json
```

结构（精简示例）：
```json
{
  "version": "0.8.0",
  "exportToModule": {
    "createRequest": "request",
    "HttpClient": "request",
    "useStorage": "storage",
    "now": "date"
  },
  "modules": {
    "request": {
      "entry": "request/index.d.ts",
      "files": ["request/types.d.ts", "request/client.d.ts", "request/plugins.d.ts", "..."],
      "values": ["createRequest", "tokenPlugin", "..."],
      "types":  ["HttpClient", "HttpConfig", "PageData", "..."]
    }
  }
}
```

用法：
- 知道 API 名（如 `createRequest`、`HttpClient`） → 查 `exportToModule[name]` 拿到模块名
- 看 `modules[name].files` 找到要读的 .d.ts 文件
- 类型定义通常在 `{module}/types.d.ts`，函数实现签名在 `{module}/{client,plugins,helpers,api}.d.ts`

manifest 不存在的回退：消费方装的是 ekit < 0.8.0 → 直接走第三步用约定路径。

### 第三步：读模块 .d.ts（精确签名 + JSDoc）

按存在性回退：

```
a. 优先：<project-root>/node_modules/@dwydev/ekit/dist/{module}/{file}.d.ts
   —— 下游消费方默认场景，含完整签名 + JSDoc 注释

b. 次选：<dwy-shared-root>/frontend/ekit/src/{module}/{file}.ts
   —— 仅当在 dwy-shared monorepo 内或并列 clone 时可用

c. 都拿不到 → 退到本文档下方的 [模块用途索引](#模块用途索引) + 总入口 dist/index.d.ts
```

### 第四步：冲突时永远信 node_modules

本 SKILL.md 是导航 + 心智模型，**不是 API 真相**。当文档描述与消费方 node_modules 中 `.d.ts` 不一致：无条件以 node_modules 为准。

---

## 版本兼容规则

- 本 skill `ekit_baseline_version: 0.8.0`，模块索引、防腐层约束、踩坑提示都基于这个版本
- ekit < 0.8.0 没有 `module-manifest.json`：直接走第三步的 .d.ts 约定路径
- 主版本号变更（0.x → 1.x）时，必须先读 `node_modules/@dwydev/ekit/dist/index.d.ts` 重建认知

---

## 防腐层硬性约束（写代码前必读）

这是 ekit **设计核心**，与版本无关。即使读了 .d.ts，也要遵守以下原则：

### 对外类型不允许出现底层库类名

```ts
// 错误：ekit 不导出底层类型
import type { AxiosInstance, IStringifyOptions, CookieAttributes } from '@dwydev/ekit'
import { dayjs } from '@dwydev/ekit'

// 正确：用 ekit 自有契约
import type { HttpClient, StringifyOptions, CookieOptions } from '@dwydev/ekit'
import { now, formatTimestamp } from '@dwydev/ekit'
```

### 业务代码禁止直接调底层 API

| 禁止 | 改用 |
|------|------|
| `new Date()` / `toLocaleString()` | `now()` / `formatTimestamp()` / `formatDateTime()` |
| `localStorage.setItem(...)` | `storage.set()` 或 `useStorage()` |
| `navigator.clipboard.writeText(...)` | `copyText()` 或 `useClipboard()` |
| `document.cookie = ...` | `cookie.set()` 或 `useCookie()` |
| `document.addEventListener('click', ...)` | `useEventListener()` |
| 手写 axios 实例 | `createRequest()` |
| 自写 debounce / throttle / clickOutside | `useDebounce()` / `useThrottle()` / `useClickOutside()` |

理由：替换底层实现（如 axios → fetch、dayjs → date-fns）时业务代码不用改，且统一封装能保证 SSR-safe / 跨标签页同步 / 边界处理等开源库已经做好的事。

---

## 重要约束与已知陷阱

源码读不出来的"踩坑经验"，每次写 ekit 代码都遵守：

### request（HTTP 客户端）

- **dwyeapi 响应契约**：用 `unwrapPlugin()` 自动解包 `{ code, message, data, timestamp }`，业务失败自动 reject。`HttpResponse<T>.data` 才是纯业务数据
- **分页**：返回类型用 `PageData<T>`（字段：`items / total / page / page_size`）
- **token 刷新**：`refreshTokenPlugin` 的 `retry: (cfg) => http.request(cfg)` **必填**，否则刷新成功后无法重放失败请求
- **业务错误捕获**：用 `isApiBusinessError(err)` 类型守卫 + `err.businessCode` 判断；表单字段错误用 `extractValidationErrors(err)` 剥离 `body./query./path.` 前缀后直接 `form.setErrors()`

### date

- ekit **不暴露** `dayjs` 实例和类型，所有日期运算走函数（`now / formatTimestamp / formatInTimezone / formatDate / formatDateTime / formatTime / formatRelativeTime / formatBy`）
- 入参 `DateInput = string | number | Date`，返回原生 `string / number / Date`

### validators

- 双层 API：布尔函数（`isPhone / isEmail / ...`）用于简单校验；**zod schemas**（`phoneSchema / emailSchema / ...`）用于 vee-validate 集成（配合 `toTypedSchema()`）
- `minLengthSchema(n)` / `maxLengthSchema(n)` 是**工厂函数**，调用后才返回 schema

### hooks

- `useFormPersist(key, initialValue, options?)` 表单刷新自动回填，**默认排除 19 项敏感字段**（password / token / code / otp 等）。需要追加：`options.exclude`；需要完全自定义：`options.disableDefaultExclude: true`
- VueUse 再导出：`useThrottle / useWindowSize / useMediaQuery / useIntersectionObserver / useResizeObserver`（直接用 VueUse 名字，不要找 ekit 自己实现的版本 — 已经废弃）
- `useDebounce` 返回 `Readonly<Ref<T>>`（不是可写 ref，过去版本是可写的，迁移时注意）

### masking

- 纯函数，无依赖
- **输入不符合格式时原样返回，不抛异常**（设计意图：不影响显示流程）

### storage / cookie

- `useStorage()` 是 VueUse 再导出，跨标签页同步 + SSR-safe + 自动 JSON 序列化
- `useCookie(key, default)` 返回 ref：`ref.value = undefined` 自动删除 cookie
- `storage.set()` / `cookie.set()` 自动 JSON.stringify，`get()` 自动 parse

### file

- `downloadFile(url, options?)` 默认 GET，自动从 Content-Disposition 解析文件名
- `requester` 选项接受任何符合 `FileRequester` 契约的对象（axios 实例天然满足）

---

## 模块用途索引

按模块导航。**只提供模块名 + 用途 + 关键导出**，精确签名一律按 [查 API 标准动作](#查-api-标准动作核心每次写-ekit-代码前都做) 读 `.d.ts`。

### request — HTTP 客户端 + dwyeapi 契约

| 类别 | 关键导出 |
|------|---------|
| 工厂 | `createRequest` |
| 内置插件 | `tokenPlugin / headerPlugin / unwrapPlugin / refreshTokenPlugin` |
| 业务常量/守卫 | `SUCCESS_CODE / isApiBusinessError / extractValidationErrors` |
| 核心类型 | `HttpClient / HttpConfig / HttpResponse<T> / HttpError / HttpPlugin / HttpMethod / HttpResponseType / CreateRequestOptions` |
| dwyeapi 契约类型 | `ApiResponse<T> / PageData<T> / ValidationFieldError / ValidationErrorData / CommonBusinessCode / BusinessCode / ApiBusinessError` |

`CommonBusinessCode` 各业务码的 HTTP 状态 + 语义 + 典型处理已写进 `request/api.d.ts` 的 JSDoc，需要时读 .d.ts。

### storage — localStorage 封装

`useStorage` (VueUse 再导出) + `storage` 静态对象（`get / set / remove / clear`）。

### cookie — Cookie 读写

`useCookie` + `cookie` 静态对象（`get / set / remove`）+ `CookieOptions` 类型。

### date — 日期/时间/时区

`now / formatTimestamp / formatInTimezone / formatRelativeTime / formatDate / formatDateTime / formatTime / formatBy`。

### validators — 表单校验

- 布尔：`isPhone / isEmail / isIdCard / isUrl / isRequired / minLength / maxLength`
- zod schemas：`phoneSchema / emailSchema / idCardSchema / urlSchema / requiredSchema / minLengthSchema / maxLengthSchema`

### copy — 剪贴板

`copyText` 快捷函数 + `useClipboard` composable（VueUse 再导出）。

### qs — 查询字符串

`stringify / parse` + `StringifyOptions / ParseOptions`。

### file — 文件下载

`downloadFile / saveBlob / formatFileSize` + `DownloadOptions / FileRequester`。

### hooks — Vue Composables

- ekit 自有：`useFormPersist / DEFAULT_SENSITIVE_FIELDS / UseFormPersistOptions / UseFormPersistReturn / useDebounce / useClickOutside / useEventListener`
- VueUse 再导出：`useThrottle / useWindowSize / useMediaQuery / useIntersectionObserver / useResizeObserver`

### masking — PII 脱敏

`maskPhone / maskEmail / maskIdCard / maskBankCard / maskName / maskAddress / maskIp / maskLicensePlate / maskText`。

每个函数的脱敏规则 + `@example` 已写进 `masking/index.d.ts` 的 JSDoc（如 `maskPhone('13812345678') → '138****5678'`），需要时读 .d.ts。
