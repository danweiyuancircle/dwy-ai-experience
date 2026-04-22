---
name: dwy-frontend-ekit
description: "@dwydev/ekit 前端工具库速查（v0.6.0）。触发条件：HTTP 请求、localStorage/Cookie、表单校验、日期/时区、剪贴板、查询字符串、文件下载、PII 脱敏、Vue composable 工具。"
---

# @dwydev/ekit 工具库速查（v0.6.0）

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

---

## request — HTTP 客户端（防腐层）

```ts
import {
  createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin,
} from '@dwydev/ekit'
import type {
  HttpClient, HttpConfig, HttpResponse, HttpError, HttpPlugin,
  HttpMethod, HttpResponseType, CreateRequestOptions,
} from '@dwydev/ekit'
```

### createRequest(options?) → HttpClient

底层是 axios，但**返回 `HttpClient` 而不是 `AxiosInstance`**。

```ts
const http: HttpClient = createRequest({
  baseURL: '/api',                       // 默认 '/api'
  timeout: 30000,                        // 默认 30000
  headers: { 'X-Client': 'web' },        // 共享默认请求头
  plugins: [
    tokenPlugin({ getToken: () => localStorage.getItem('token') }),
    unwrapPlugin(),
  ],
})

// HttpClient 接口
const res = await http.get<User>('/users/1')           // res: HttpResponse<User>
const res = await http.post<User>('/users', { ... })
const res = await http.request({ method: 'PUT', url: '/users/1', data })
// 还有 put / delete / patch / head
```

### HttpConfig / HttpResponse / HttpError

```ts
interface HttpConfig {
  url?: string
  method?: HttpMethod                     // 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'
  baseURL?: string
  headers?: Record<string, string>
  params?: Record<string, any>
  data?: any
  timeout?: number
  responseType?: HttpResponseType         // 'json' | 'blob' | 'text' | 'arraybuffer'
  extra?: Record<string, unknown>         // 逃生舱：透传 axios 特有配置
}

interface HttpResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: Record<string, string>
  config: HttpConfig
}

interface HttpError<T = any> extends Error {
  config?: HttpConfig
  response?: HttpResponse<T>
  code?: string
}
```

### HttpPlugin 接口

```ts
interface HttpPlugin {
  onRequest?: (config: HttpConfig) => HttpConfig | Promise<HttpConfig>
  onResponse?: (response: HttpResponse) => HttpResponse | Promise<HttpResponse>
  // 返回非 undefined 视为已恢复，终止后续插件
  onResponseError?: (error: HttpError) => any
}
```

> 旧版的 `RequestPlugin` 已重命名为 `HttpPlugin`，所有钩子参数类型从 axios 类型改为 ekit 自有契约。

### 内置插件

| 插件 | 用途 | 参数 |
|------|------|------|
| `tokenPlugin` | 注入 `Authorization: Bearer <token>` | `{ getToken: () => string \| null }` |
| `headerPlugin` | 注入自定义动态 header | `{ name: string, getValue: () => string \| null }` |
| `unwrapPlugin` | 解包 `{ code, data, message }`，code !== 200 时 reject；非该格式原样透传 | 无 |
| `refreshTokenPlugin` | 401 自动刷新并重放 | 见下 |

### refreshTokenPlugin（带 retry 注入）

新版需要传 `retry`，因为插件不再持有 client 引用：

```ts
let http: HttpClient
http = createRequest({
  plugins: [
    tokenPlugin({ getToken: () => localStorage.getItem('token') }),
    refreshTokenPlugin({
      getRefreshToken: () => localStorage.getItem('refreshToken'),
      refreshFn: async (refreshToken) => {
        const res = await http.post<{ token: string }>('/auth/refresh', { refreshToken })
        localStorage.setItem('token', res.data.token)
        return res.data.token
      },
      onRefreshFail: () => {
        localStorage.clear()
        window.location.href = '/login'
      },
      retry: (cfg) => http.request(cfg),       // 必填：重放请求
      isLoginUrl: (url) => url.includes('/auth/login'),  // 可选
    }),
    unwrapPlugin(),
  ],
})
```

---

## storage — localStorage

```ts
import { useStorage, storage } from '@dwydev/ekit'
```

### useStorage(key, defaultValue) — 直接再导出 @vueuse/core

跨标签页同步、SSR-safe、自动 JSON 序列化。**API 与 VueUse 一致**（不再是 ekit 自写）。

```ts
const token = useStorage<string>('token', '')
const config = useStorage('config', { theme: 'light' }, localStorage, { mergeDefaults: true })
```

### storage — 静态对象（非组件场景）

| 方法 | 签名 |
|------|------|
| `get<T>(key, defaultValue?)` | 返回 `T \| undefined`，JSON 解析失败按字符串返回 |
| `set(key, value)` | 自动 `JSON.stringify` |
| `remove(key)` | 删除 |
| `clear()` | 清空全部（慎用） |

---

## cookie — Cookie 读写

```ts
import { useCookie, cookie } from '@dwydev/ekit'
import type { CookieOptions } from '@dwydev/ekit'   // 旧名 CookieAttributes 已废弃
```

### CookieOptions

```ts
interface CookieOptions {
  expires?: number | Date              // 天数或 Date；不传 = 会话级
  path?: string                        // 默认 '/'
  domain?: string
  secure?: boolean                     // 仅 HTTPS
  sameSite?: 'strict' | 'lax' | 'none'
}
```

### cookie（静态）

```ts
cookie.get<User>('user')
cookie.set('user', { id: 1, name: 'Alice' }, { expires: 7, secure: true })
cookie.remove('user', { path: '/' })   // 删除时 path/domain 必须与写入一致
```

### useCookie(key, defaultValue?) → Ref

```ts
const lang = useCookie('lang', 'zh-CN')
lang.value = 'en-US'        // 自动写入 cookie
lang.value = undefined       // 自动删除
```

---

## date — 日期 / 时间 / 时区

```ts
import {
  now, formatTimestamp, formatInTimezone,
  formatDate, formatDateTime, formatTime, formatRelativeTime, formatBy,
} from '@dwydev/ekit'
```

底层是 dayjs（含 utc + timezone + relativeTime + zh-cn locale 插件），**不导出 dayjs 实例**。所有函数对外用 `string | number | Date`。

### 时间戳工具（v0.6.0 新增）

| 函数 | 签名 | 说明 |
|------|------|------|
| `now()` | `(): number` | 当前 UTC Unix 毫秒戳，等价于 `Date.now()` |
| `formatTimestamp(ts, fmt?)` | `(ts: number, fmt?: string): string` | 把毫秒戳格式化为本地时区字符串。默认 `'YYYY-MM-DD HH:mm:ss'` |
| `formatInTimezone(tz, ts?, fmt?)` | `(tz: string, ts?: number, fmt?: string): string` | 在指定 IANA 时区下格式化（如 `'Asia/Shanghai'` / `'America/New_York'` / `'UTC'`），ts 不传用当前时间 |

```ts
const ts = now()                                         // 1745318445000
formatTimestamp(ts)                                      // '2026-04-22 18:40:45'
formatTimestamp(ts, 'YYYY/MM/DD')                        // '2026/04/22'
formatInTimezone('America/New_York', ts)                 // '2026-04-22 06:40:45'
formatInTimezone('UTC', ts, 'HH:mm')                     // '10:40'
```

### 普通格式化

| 函数 | 输出 | 输入 |
|------|------|------|
| `formatDate(input)` | `YYYY-MM-DD` | `string \| number \| Date` |
| `formatDateTime(input)` | `YYYY-MM-DD HH:mm:ss` | 同上 |
| `formatTime(input)` | `HH:mm` | 同上 |
| `formatRelativeTime(input)` | `刚刚` / `N 分钟前` / `N 小时前` / `N 天前`；> 30 天退化为 `YYYY-MM-DD` | 同上 |
| `formatBy(input, template)` | 自定义 dayjs 模板 | `formatBy(ts, 'YYYY年MM月DD日')` → `2026年04月22日` |

---

## validators — 表单校验

```ts
import {
  isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength,
  // 也可用 zod schema 配合 vee-validate
  phoneSchema, emailSchema, idCardSchema, urlSchema,
  requiredSchema, minLengthSchema, maxLengthSchema,
} from '@dwydev/ekit'
```

### 布尔校验函数

| 函数 | 签名 | 规则 |
|------|------|------|
| `isPhone(value)` | `string => boolean` | 中国手机号 1[3-9] 开头 11 位 |
| `isEmail(value)` | `string => boolean` | 基础邮箱 |
| `isIdCard(value)` | `string => boolean` | 18 位身份证（末位允许 X/x） |
| `isUrl(value)` | `string => boolean` | 合法 URL |
| `isRequired(value)` | `any => boolean` | 非空（0 / false 视为有效） |
| `minLength(value, n)` | `(string, number) => boolean` | 最小长度 |
| `maxLength(value, n)` | `(string, number) => boolean` | 最大长度 |

### Zod schema（配合 vee-validate）

```ts
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { phoneSchema, emailSchema } from '@dwydev/ekit'

const schema = toTypedSchema(z.object({
  phone: phoneSchema,
  email: emailSchema,
}))
const { defineField, errors } = useForm({ validationSchema: schema })
```

> `minLengthSchema(n)` / `maxLengthSchema(n)` 是工厂函数，调用后返回 schema。

---

## copy — 剪贴板

```ts
import { copyText, useClipboard } from '@dwydev/ekit'
```

### copyText(text)

非组件场景一次性复制：

```ts
await copyText('hello')
```

### useClipboard — 直接再导出 @vueuse/core

```ts
const { text, copy, copied, isSupported } = useClipboard({ source: '', copiedDuring: 1500 })
copy('hello')
// copied: ComputedRef<boolean>，1500ms 后自动复位
// isSupported: ComputedRef<boolean>，注意是 computed 不是 ref
```

> 旧版 ekit 自写的 `useClipboard` 返回结构略有不同，迁移时需对照新签名。

---

## qs — 查询字符串

```ts
import { stringify, parse } from '@dwydev/ekit'
import type { StringifyOptions, ParseOptions } from '@dwydev/ekit'   // 旧名 IStringifyOptions / IParseOptions 已废弃
```

```ts
stringify({ ids: [1, 2], name: 'a' })                       // 'ids=1&ids=2&name=a'  默认 arrayFormat: 'repeat'
stringify({ ids: [1, 2] }, { arrayFormat: 'brackets' })     // 'ids[]=1&ids[]=2'
stringify({ a: 1 }, { addQueryPrefix: true })               // '?a=1'

parse('?a=1&b=2')                                            // { a: '1', b: '2' }   默认 ignoreQueryPrefix: true
parse('a.b=1', { allowDots: true })                          // { a: { b: '1' } }
```

### StringifyOptions / ParseOptions

```ts
interface StringifyOptions {
  arrayFormat?: 'repeat' | 'brackets' | 'indices' | 'comma'
  addQueryPrefix?: boolean
  skipNulls?: boolean
}
interface ParseOptions {
  ignoreQueryPrefix?: boolean
  allowDots?: boolean
}
```

---

## file — 文件下载 / Blob / 文件大小

```ts
import { downloadFile, saveBlob, formatFileSize } from '@dwydev/ekit'
import type { DownloadOptions, FileRequester } from '@dwydev/ekit'   // requester 不是 requestInstance
```

### downloadFile(url, options?)

```ts
await downloadFile('/api/export.xlsx')                                // GET，自动从 Content-Disposition 解析文件名
await downloadFile('/api/export', {
  filename: '报表.xlsx',
  method: 'POST',
  data: { dateRange: [start, end] },
  headers: { Authorization: `Bearer ${token}` },
})

// 用自己的 HTTP 客户端发请求（不传则动态 import axios）
await downloadFile('/api/export', { requester: myAxiosInstance })
```

### FileRequester 契约

任何满足以下结构的对象都可以作为 requester（axios 实例天然满足）：

```ts
interface FileRequester {
  request(config: {
    url: string
    method?: 'GET' | 'POST'
    data?: any
    headers?: Record<string, string>
    responseType: 'blob'
  }): Promise<{
    data: Blob | ArrayBuffer
    headers?: Record<string, string | undefined>
  }>
}
```

> 旧版字段 `requestInstance: AxiosInstance` 已改名 `requester: FileRequester`，类型不再泄露 axios。

### 其他

```ts
saveBlob(blob, 'data.json')               // 直接保存已有 Blob
formatFileSize(1234567)                    // '1.18 MB'
formatFileSize(1234567, 0)                 // '1 MB'
```

---

## hooks — Vue Composables

**全部再导出 `@vueuse/core`**，ekit 不再自写。从 `@dwydev/ekit` 主入口导入即可：

```ts
import {
  // src/hooks/index.ts
  useDebounce, useClickOutside, useEventListener,
  // src/hooks/vueuse.ts
  useThrottle, useWindowSize, useMediaQuery, useIntersectionObserver, useResizeObserver,
} from '@dwydev/ekit'
```

| ekit 名 | VueUse 实现 | 说明 |
|---------|-------------|------|
| `useDebounce(value, delay=300)` | `refDebounced` | 默认 300ms（VueUse 默认 200ms） |
| `useClickOutside(target, handler)` | `onClickOutside` | 点击元素外部触发 |
| `useEventListener(target, event, handler, options?)` | 同名 | 自动绑/解绑，支持 `Ref<EventTarget>` |
| `useThrottle(fn, ms)` | `useThrottleFn` | 节流函数 |
| `useWindowSize()` | 同名 | `{ width, height }` |
| `useMediaQuery(query)` | 同名 | `useMediaQuery('(max-width: 768px)')` |
| `useIntersectionObserver(target, cb)` | 同名 | 监听元素出现/消失 |
| `useResizeObserver(target, cb)` | 同名 | 监听元素尺寸变化 |

> 旧版 ekit 自写的 `useDebounce` 返回普通 `Ref<T>`，新版返回 VueUse 的 `Readonly<Ref<T>>`，**不能** `debouncedSearch.value = '...'`。

---

## masking — PII 脱敏

```ts
import {
  maskPhone, maskEmail, maskIdCard, maskBankCard,
  maskName, maskAddress, maskIp, maskLicensePlate, maskText,
} from '@dwydev/ekit'
```

纯函数，无外部依赖。**输入不符合格式时原样返回，不抛异常**。

| 函数 | 规则 | 示例 |
|------|------|------|
| `maskPhone(phone)` | 前 3 后 4 | `'138****5678'` |
| `maskEmail(email)` | 首字符 + `***` + @域名 | `'z***@gmail.com'` |
| `maskIdCard(id)` | 前 3 后 4（18 位） | `'420***********1234'` |
| `maskBankCard(card)` | 前 4 后 4（13~19 位） | `'6222********1234'` |
| `maskName(name)` | 2 字 → 姓+`*`；3+ 字 → 姓+`*`×(n-2)+末字 | `'张*'` / `'张*明'` |
| `maskAddress(addr)` | 保留省/市/区/县/镇/旗前缀 + `****` | `'浙江省杭州市西湖区****'` |
| `maskIp(ip)` | IPv4 末段替换 `*` | `'192.168.1.*'` |
| `maskLicensePlate(plate)` | 前 2 后 1，中间 `***` | `'浙A***8'` |
| `maskText(text, start=1, end=1, ch='*')` | 通用：保留首尾 N 位 | `maskText('1234567890', 2, 3)` → `'12*****890'` |

---

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
