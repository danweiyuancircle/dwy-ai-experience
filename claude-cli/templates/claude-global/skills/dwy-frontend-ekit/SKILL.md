---
name: dwy-frontend-ekit
description: "@danweiyuan/ekit 前端工具库速查。触发条件：需要 HTTP 请求封装、localStorage、表单校验、日期格式化、Vue composable 工具时。"
---

# @danweiyuan/ekit 工具库速查

Vue 3 项目通用工具库，包含 5 个模块：request、storage、validators、date、hooks。

## 安装

```bash
pnpm add @danweiyuan/ekit
# peerDependencies: axios ^1.0.0, vue ^3.4.0
```

```ts
import { createRequest, useStorage, isPhone, formatDate, useDebounce } from '@danweiyuan/ekit'
```

## 查阅源码

每个模块源码在 `frontend/ekit/src/{module}/index.ts`，函数简短可直接阅读。

---

## request — Axios 插件化封装

```ts
import { createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin } from '@danweiyuan/ekit'
```

### createRequest(options?)

创建带插件系统的 Axios 实例。插件按顺序执行请求/响应拦截。

```ts
const http = createRequest({
  baseURL: '/api',      // 默认 '/api'
  timeout: 30000,       // 默认 30000
  plugins: [
    tokenPlugin({ getToken: () => localStorage.getItem('token') }),
    unwrapPlugin(),
  ],
})
```

### 内置插件

| 插件 | 用途 | 参数 |
|------|------|------|
| tokenPlugin | 自动注入 Bearer token | `{ getToken: () => string \| null }` |
| headerPlugin | 注入自定义请求头 | `{ name: string, getValue: () => string \| null }` |
| unwrapPlugin | 解包 `{ code, data, message }` 响应，code !== 200 时 reject | 无参数 |
| refreshTokenPlugin | 401 自动刷新 token 并重试 | `{ getRefreshToken, refreshFn, onRefreshFail, isLoginUrl? }` |

### RequestPlugin 接口

```ts
interface RequestPlugin {
  onRequest?: (config: InternalAxiosRequestConfig) => config | Promise<config>
  onResponse?: (response: AxiosResponse) => response | Promise<response>
  onResponseError?: (error: AxiosError) => any
}
```

### refreshTokenPlugin 详解

```ts
refreshTokenPlugin({
  getRefreshToken: () => localStorage.getItem('refreshToken'),
  refreshFn: async (refreshToken) => {
    // 调用刷新接口，返回新 access token
    const { data } = await http.post('/auth/refresh', { refreshToken })
    localStorage.setItem('token', data.token)
    return data.token
  },
  onRefreshFail: () => {
    // 刷新失败，跳转登录
    localStorage.clear()
    window.location.href = '/login'
  },
  isLoginUrl: (url) => url.includes('/auth/login'), // 可选，默认检测 /auth/login
})
```

---

## storage — localStorage 封装

```ts
import { useStorage, storage } from '@danweiyuan/ekit'
```

### useStorage(key, defaultValue) — 响应式

返回 Vue `Ref<T>`，自动 JSON 序列化，深度 watch 自动同步。设为 null/undefined 时自动 removeItem。

```ts
const token = useStorage<string>('token', '')
const config = useStorage<{ theme: string }>('config', { theme: 'light' })
```

### storage — 静态工具对象

| 方法 | 签名 | 说明 |
|------|------|------|
| get | `get<T>(key, defaultValue?): T \| undefined` | JSON 解析失败时返回原始字符串 |
| set | `set(key, value): void` | JSON.stringify 后存储 |
| remove | `remove(key): void` | 删除指定 key |
| clear | `clear(): void` | 清空全部 |

---

## validators — 校验函数

```ts
import { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from '@danweiyuan/ekit'
```

| 函数 | 签名 | 规则 |
|------|------|------|
| isPhone | `(value: string) => boolean` | 中国手机号 1[3-9]开头 11 位 |
| isEmail | `(value: string) => boolean` | 基础邮箱格式 |
| isIdCard | `(value: string) => boolean` | 18 位身份证（末位可为 X/x） |
| isUrl | `(value: string) => boolean` | 使用 `new URL()` 校验 |
| isRequired | `(value: any) => boolean` | 非 null/undefined/空字符串/空数组。0 和 false 视为有效 |
| minLength | `(value: string, min: number) => boolean` | 最小长度 |
| maxLength | `(value: string, max: number) => boolean` | 最大长度 |

---

## date — 日期格式化

```ts
import { formatDate, formatDateTime, formatTime, formatRelativeTime, formatBy } from '@danweiyuan/ekit'
```

所有函数接收 `string | number | Date` 类型输入。

| 函数 | 输出格式 | 示例 |
|------|---------|------|
| formatDate | `YYYY-MM-DD` | `2025-03-15` |
| formatDateTime | `YYYY-MM-DD HH:mm:ss` | `2025-03-15 14:30:00` |
| formatTime | `HH:mm` | `14:30` |
| formatRelativeTime | 中文相对时间 | `刚刚` / `5 分钟前` / `3 小时前` / `7 天前` / 超过 30 天返回 `YYYY-MM-DD` |
| formatBy | 自定义 dayjs 模板 | `formatBy(date, 'YYYY年MM月DD日')` → `2025年03月15日` |

---

## hooks — Vue Composables

```ts
import { useDebounce, useClickOutside, useEventListener } from '@danweiyuan/ekit'
```

### useDebounce(value, delay?)

```ts
const search = ref('')
const debouncedSearch = useDebounce(search, 300) // 默认 300ms
```

返回防抖后的 `Ref<T>`，仅在源值停止变化 delay 毫秒后更新。

### useClickOutside(target, handler)

```ts
const popoverRef = ref<HTMLElement | null>(null)
useClickOutside(popoverRef, () => { isOpen.value = false })
```

点击 target 元素外部时触发 handler。自动在 onMounted/onBeforeUnmount 绑定/解绑。

### useEventListener(target, event, handler, options?)

```ts
useEventListener(window, 'resize', onResize)
useEventListener(elementRef, 'scroll', onScroll, { passive: true })
```

target 可以是 `EventTarget` 或 `Ref<EventTarget>`。自动在 onMounted/onBeforeUnmount 绑定/解绑。
