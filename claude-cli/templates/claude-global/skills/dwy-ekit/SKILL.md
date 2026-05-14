---
name: dwy-ekit
description: "【强制速查】只要涉及以下任何主题，必须调用本 skill，无论用户是否说ekit：HTTP 请求 / axios 封装 / token 刷新 / dwyeapi 响应契约对接 / localStorage / Cookie / useStorage / useCookie / 日期格式化 / 时区处理 / dayjs / 表单校验 / zod schema / vee-validate / PII 脱敏 / 剪贴板 / useClipboard / 文件下载 / Blob / 查询字符串 / qs / Vue composables（debounce / throttle / click-outside / event-listener / window-size / media-query / intersection-observer / resize-observer / useFormPersist）。本 skill 是 @dwydev/ekit（v0.7.0）的唯一权威来源，禁止绕过 ekit 直接手写底层 API。"
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
// 错误：ekit 不导出底层类型
import type { AxiosInstance, IStringifyOptions, CookieAttributes } from '@dwydev/ekit'
import { dayjs } from '@dwydev/ekit'

// 正确：用 ekit 自有契约
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
