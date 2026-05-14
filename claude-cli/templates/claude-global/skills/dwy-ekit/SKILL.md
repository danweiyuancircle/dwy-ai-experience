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

## 模块速查

### request — HTTP 客户端 + 4 内置插件 + dwyeapi 契约

```ts
import {
  createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin,
  SUCCESS_CODE, isApiBusinessError, extractValidationErrors,
} from '@dwydev/ekit'
import type {
  HttpClient, HttpConfig, HttpResponse, HttpError, HttpPlugin,
  CreateRequestOptions, ApiResponse, PageData,
} from '@dwydev/ekit'
```

**createRequest**

```ts
const http: HttpClient = createRequest({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'X-Client': 'web' },
  plugins: [tokenPlugin({ getToken: () => localStorage.getItem('token') }), unwrapPlugin()],
})

const res = await http.get<User>('/users/1')        // res: HttpResponse<User>
const list = await http.get<PageData<User>>('/users')
list.data.items       // User[]
list.data.total       // number
list.data.page        // number
list.data.page_size   // number
```

**内置插件**

| 插件 | 参数 | 说明 |
|------|------|------|
| `tokenPlugin` | `{ getToken: () => string | null }` | 注入 `Authorization: Bearer <token>` |
| `headerPlugin` | `{ name, getValue }` | 动态自定义 header |
| `unwrapPlugin` | 无 | 解包 dwyeapi `{ code, message, data, timestamp }`，业务失败时 reject |
| `refreshTokenPlugin` | `{ getRefreshToken, refreshFn, onRefreshFail, retry, isLoginUrl? }` | 401 自动刷新并重放；`retry: (cfg) => http.request(cfg)` 必填 |

**响应契约 & 错误捕获**

```ts
// unwrap 后 data 是纯业务数据（单体）或 PageData<T>（分页）
const res = await http.get<User>('/users/1')   // res.data: User

// 捕获业务错误
try {
  await http.post('/orders', body)
} catch (err) {
  if (!isApiBusinessError(err)) { message.error('网络异常'); return }
  switch (err.businessCode) {
    case 'INSUFFICIENT_BALANCE': showRecharge(); break
    case 'VALIDATION_ERROR': form.setErrors(extractValidationErrors(err)); break
    default: message.error(err.message)
  }
}
```

`extractValidationErrors` 剥离 `body. / query. / path.` 前缀，返回 `{ field: message }` 扁平对象，与 vee-validate 的 `form.setErrors` 直接兼容。

### storage — localStorage

```ts
import { useStorage, storage } from '@dwydev/ekit'
```

| API | 签名 / 说明 |
|-----|------------|
| `useStorage(key, defaultValue, storage?, opts?)` | 再导出 @vueuse/core；跨标签页同步、SSR-safe、自动 JSON 序列化 |
| `storage.get<T>(key, defaultValue?)` | 返回 `T | undefined`；JSON 解析失败按字符串返回 |
| `storage.set(key, value)` | 自动 `JSON.stringify` |
| `storage.remove(key)` | 删除 |
| `storage.clear()` | 清空全部（慎用） |

```ts
const token = useStorage<string>('token', '')
const config = useStorage('config', { theme: 'light' }, localStorage, { mergeDefaults: true })
```

### cookie — Cookie 读写

```ts
import { useCookie, cookie } from '@dwydev/ekit'
import type { CookieOptions } from '@dwydev/ekit'
```

```ts
interface CookieOptions {
  expires?: number | Date   // 天数或 Date；不传 = 会话级
  path?: string             // 默认 '/'
  domain?: string
  secure?: boolean
  sameSite?: 'strict' | 'lax' | 'none'
}

cookie.get<User>('user')
cookie.set('user', { id: 1 }, { expires: 7, secure: true })
cookie.remove('user', { path: '/' })

const lang = useCookie('lang', 'zh-CN')
lang.value = 'en-US'       // 自动写入
lang.value = undefined     // 自动删除
```

### date — 日期 / 时间 / 时区

```ts
import {
  now, formatTimestamp, formatInTimezone,
  formatDate, formatDateTime, formatTime, formatRelativeTime, formatBy,
} from '@dwydev/ekit'
```

| 函数 | 签名 | 输出示例 |
|------|------|---------|
| `now()` | `(): number` | `1745318445000`（UTC 毫秒戳） |
| `formatTimestamp(ts, fmt?)` | `(number, string?) => string` | `'2026-04-22 18:40:45'`（默认） |
| `formatInTimezone(tz, ts?, fmt?)` | `(string, number?, string?) => string` | `formatInTimezone('America/New_York', ts)` |
| `formatDate(input)` | `(string | number | Date) => string` | `'2026-04-22'` |
| `formatDateTime(input)` | 同上 | `'2026-04-22 18:40:45'` |
| `formatTime(input)` | 同上 | `'18:40'` |
| `formatRelativeTime(input)` | 同上 | `'刚刚' / '5 分钟前' / '3 小时前' / '2 天前'`；> 30 天退化为 `YYYY-MM-DD` |
| `formatBy(input, template)` | 同上 | `formatBy(ts, 'YYYY年MM月DD日')` -> `'2026年04月22日'` |

### qs — 查询字符串

```ts
import { stringify, parse } from '@dwydev/ekit'
import type { StringifyOptions, ParseOptions } from '@dwydev/ekit'
```

```ts
stringify({ ids: [1, 2], name: 'a' })                          // 'ids=1&ids=2&name=a'
stringify({ ids: [1, 2] }, { arrayFormat: 'brackets' })        // 'ids[]=1&ids[]=2'
stringify({ a: 1 }, { addQueryPrefix: true })                  // '?a=1'

parse('?a=1&b=2')                                              // { a: '1', b: '2' }（默认 ignoreQueryPrefix: true）
parse('a.b=1', { allowDots: true })                            // { a: { b: '1' } }
```

### validators — 表单校验

```ts
import {
  isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength,
  phoneSchema, emailSchema, idCardSchema, urlSchema,
  requiredSchema, minLengthSchema, maxLengthSchema,
} from '@dwydev/ekit'
```

**布尔函数**

| 函数 | 规则 |
|------|------|
| `isPhone(value)` | 中国手机号 1[3-9] 开头 11 位 |
| `isEmail(value)` | 基础邮箱格式 |
| `isIdCard(value)` | 18 位身份证（末位允许 X/x） |
| `isUrl(value)` | 合法 URL |
| `isRequired(value)` | 非空（0 / false 视为有效） |
| `minLength(value, n)` / `maxLength(value, n)` | 长度校验 |

**zod schema（配合 vee-validate）**

```ts
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { phoneSchema, emailSchema } from '@dwydev/ekit'

const schema = toTypedSchema(z.object({ phone: phoneSchema, email: emailSchema }))
const { defineField, errors } = useForm({ validationSchema: schema })
```

> `minLengthSchema(n)` / `maxLengthSchema(n)` 是工厂函数，调用后返回 schema。

### masking — PII 脱敏

```ts
import {
  maskPhone, maskEmail, maskIdCard, maskBankCard,
  maskName, maskAddress, maskIp, maskLicensePlate, maskText,
} from '@dwydev/ekit'
```

纯函数，无外部依赖。**输入不符合格式时原样返回，不抛异常**。

| 函数 | 示例输出 |
|------|---------|
|  |  |
|  |  |
|  |  |
|  |  |
|  /  |  /  |
|  |  |
|  |  |
|  |  |
|  |  |

### copy — 剪贴板

```ts
import { copyText, useClipboard } from '@dwydev/ekit'
```

```ts
await copyText('hello')

const { text, copy, copied, isSupported } = useClipboard({ source: '', copiedDuring: 1500 })
copy('hello')
// copied: ComputedRef<boolean>，1500ms 后自动复位
// isSupported: ComputedRef<boolean>
```

### file — 文件下载 / Blob / 文件大小

```ts
import { downloadFile, saveBlob, formatFileSize } from '@dwydev/ekit'
import type { DownloadOptions, FileRequester } from '@dwydev/ekit'
```

```ts
await downloadFile('/api/export.xlsx')                      // GET，自动解析文件名
await downloadFile('/api/export', {
  filename: '报表.xlsx', method: 'POST', data: { dateRange },
})

// 自定义 requester（axios 实例天然满足 FileRequester）
await downloadFile('/api/export', { requester: myHttpClient })

saveBlob(blob, 'data.json')
formatFileSize(1234567)        // '1.18 MB'
formatFileSize(1234567, 0)     // '1 MB'
```

### hooks — Vue Composables

```ts
import {
  useDebounce, useClickOutside, useEventListener, useThrottle,
  useWindowSize, useMediaQuery, useIntersectionObserver, useResizeObserver,
  useFormPersist, DEFAULT_SENSITIVE_FIELDS,
} from '@dwydev/ekit'
```

| Composable | 说明 |
|-----------|------|
| `useDebounce(value, delay=300)` | 防抖 ref；返回 `Readonly<Ref<T>>` |
| `useClickOutside(target, handler)` | 点击元素外部触发 |
| `useEventListener(target, event, handler, options?)` | 自动绑/解绑 |
| `useThrottle(fn, ms)` | 节流函数 |
| `useWindowSize()` | `{ width, height }` |
| `useMediaQuery(query)` | `useMediaQuery('(max-width: 768px)')` |
| `useIntersectionObserver(target, cb)` | 监听元素出现/消失 |
| `useResizeObserver(target, cb)` | 监听元素尺寸变化 |
| `useFormPersist(key, initialValue, options?)` | 表单刷新自动回填；默认排除敏感字段 |

**useFormPersist**

```ts
const { form, reset, clear } = useFormPersist('register-form', {
  email: '', code: '', remark: '',
})

// 选项
interface UseFormPersistOptions<T> {
  exclude?: (keyof T)[]           // 追加敏感字段
  storage?: 'session' | 'local'   // 默认 'session'
  disableDefaultExclude?: boolean // 默认 false（开启内置排除）
}

// 提交成功后清空残留
await api.register(form.value)
reset()
```

内置 `DEFAULT_SENSITIVE_FIELDS` 包含 password / confirmPassword / oldPassword / newPassword / pwd / code / captcha / verifyCode / verificationCode / smsCode / emailCode / phoneCode / otp / token / accessToken / refreshToken / signSecret / secret / apiKey 共 19 项，不区分大小写。

## 何时读取 references

本 SKILL.md 正文已包含 10 个模块的核心 API、签名和典型用法，满足 90% 编码场景。`references/` 目录保存边缘细节，仅在需要时读取：

| 文件 | 内容 |
|------|------|
| `references/request.md` | `HttpPlugin` 完整接口、`HttpError` 字段详情、refreshTokenPlugin 完整参数、`CommonBusinessCode` 枚举、非标准响应兜底行为 |
| `references/data.md` | `StringifyOptions` / `ParseOptions` 完整字段、`CookieOptions` 完整字段、useStorage 全部选项 |
| `references/form.md` | validators 底层正则规则、masking 边界处理说明 |
| `references/ui.md` | `FileRequester` 完整契约、`DownloadOptions` 全部字段、旧版迁移陷阱 |

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
