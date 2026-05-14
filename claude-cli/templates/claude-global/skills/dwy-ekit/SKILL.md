---
name: dwy-ekit
description: "@dwydev/ekit 前端工具库速查（v0.7.0）。触发条件：HTTP 请求、dwyeapi 响应契约对接、localStorage/Cookie、表单校验、日期/时区、剪贴板、查询字符串、文件下载、PII 脱敏、Vue composable 工具。"
---

# @dwydev/ekit 工具库速查（v0.7.0）

Vue 3 项目通用工具库，**薄封装层**：底层用 axios / dayjs / zod / js-cookie / qs / file-saver / @vueuse/core，**对外只暴露 ekit 自有契约**，不泄露底层库类型。

包含 10 个模块：`request` / `storage` / `cookie` / `date` / `validators` / `copy` / `qs` / `file` / `hooks` / `masking`。

## 安装

```bash
pnpm add @dwydev/ekit
# peerDependencies: vue ^3.5.0, axios ^1.0.0, dayjs ^1.11.0, zod ^3.25.0, @vueuse/core ^14.2.1
```

```ts
import {
  createRequest, useStorage, useCookie,
  formatDateTime, isPhone, copyText, stringify, downloadFile,
  useDebounce, maskPhone,
} from '@dwydev/ekit'
```

## 防腐层硬性约束（写代码前必读）

ekit 对外类型 **不允许** 出现底层库类名。下面这些导入 **会失败** —— 因为 ekit 不再 re-export：

```ts
// ❌ 错误：ekit 不导出底层类型
import type { AxiosInstance, IStringifyOptions, CookieAttributes } from '@dwydev/ekit'
import { dayjs } from '@dwydev/ekit'

// ✅ 正确：用 ekit 自有契约
import type { HttpClient, StringifyOptions, CookieOptions } from '@dwydev/ekit'
import { now, formatTimestamp } from '@dwydev/ekit'  // 不需要 dayjs 实例
```

业务代码也 **禁止** 直接调底层 API：

| 禁止 | 改用 |
|------|------|
| `new Date()` / `toLocaleString()` | `now()` / `formatTimestamp()` / `formatDateTime()` |
| `localStorage.setItem(...)` | `storage.set()` 或 `useStorage()` |
| `navigator.clipboard.writeText(...)` | `copyText()` 或 `useClipboard()` |
| `document.cookie = ...` | `cookie.set()` 或 `useCookie()` |
| `document.addEventListener('click', ...)` | `useEventListener()` |
| 手写 axios 实例 | `createRequest()` |

## 查阅源码

每个模块源码在 `/Users/chances/WebstormProjects/dwy-shared/frontend/ekit/src/{module}/`，函数都很短可以直接读。

## 模块索引

按需读取对应 references 文件，避免一次性加载全部 API 文档。

| 模块 | 用途 | 详见 |
|---|---|---|
| `request` | HTTP 客户端（防腐层 + 4 个内置插件 + dwyeapi 响应契约 + 业务错误捕获） | `references/request.md` |
| `storage` | localStorage 封装（@vueuse/core 的 useStorage + 静态 storage 对象） | `references/data.md` § storage |
| `cookie` | Cookie 读写（js-cookie 薄封装 + useCookie） | `references/data.md` § cookie |
| `date` | 日期 / 时间 / 时区格式化（基于 dayjs，不暴露实例） | `references/data.md` § date |
| `qs` | 查询字符串序列化 / 解析（基于 qs） | `references/data.md` § qs |
| `validators` | 表单校验（布尔函数 + zod schema 配合 vee-validate） | `references/form.md` § validators |
| `masking` | PII 数据脱敏（手机/邮箱/身份证/银行卡/姓名/地址等） | `references/form.md` § masking |
| `copy` | 剪贴板（copyText + @vueuse/core 的 useClipboard） | `references/ui.md` § copy |
| `file` | 文件下载 / Blob / 文件大小格式化 | `references/ui.md` § file |
| `hooks` | Vue Composables（全部再导出 @vueuse/core） | `references/ui.md` § hooks |

## v0.6.0 迁移要点

| 旧 | 新 |
|----|----|
| `createRequest(): AxiosInstance` | `createRequest(): HttpClient` |
| `RequestPlugin` | `HttpPlugin` |
| `import { dayjs } from '@dwydev/ekit'` | 用 `now / formatTimestamp / formatInTimezone / formatDateTime` 等函数 |
| `CookieAttributes` | `CookieOptions` |
| `IStringifyOptions / IParseOptions` | `StringifyOptions / ParseOptions` |
| `DownloadOptions.requestInstance: AxiosInstance` | `DownloadOptions.requester: FileRequester` |
| 自写 `useDebounce` 返回可写 `Ref` | VueUse `refDebounced` 返回 `Readonly<Ref>` |
| 自写 `useClipboard` 返回 `{ text, copy, copied, isSupported }`（isSupported 是 boolean） | VueUse 版（isSupported 是 `ComputedRef<boolean>`） |
| `refreshTokenPlugin` 自动重放 | 必须传 `retry: (cfg) => client.request(cfg)` |
