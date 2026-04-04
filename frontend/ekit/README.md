# @danweiyuan/ekit

Vue 3 通用工具库：HTTP 请求插件、本地存储、日期格式化、表单校验、常用 Hooks。不包含 UI 组件，可独立用于任意 Vue 3 项目。

## 安装

```bash
npm install @danweiyuan/ekit
```

**Peer dependencies:** `vue ^3.4`, `axios ^1.0`

---

## 模块

### request — Axios 实例工厂

```ts
import {
  createRequest,
  tokenPlugin,
  headerPlugin,
  unwrapPlugin,
  refreshTokenPlugin,
} from '@danweiyuan/ekit'
import type { RequestPlugin, CreateRequestOptions } from '@danweiyuan/ekit'
```

#### `createRequest(options?: CreateRequestOptions): AxiosInstance`

创建预置插件链的 Axios 实例。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `baseURL` | `string` | `'/api'` | 请求基础路径 |
| `timeout` | `number` | `30000` | 超时毫秒数 |
| `plugins` | `RequestPlugin[]` | `[]` | 拦截器插件列表，按顺序执行 |

```ts
const http = createRequest({
  baseURL: '/api',
  timeout: 15000,
  plugins: [tokenPlugin({ getToken: () => localStorage.getItem('token') }), unwrapPlugin()],
})
```

#### 内置插件

| 函数 | 说明 |
|------|------|
| `tokenPlugin({ getToken })` | 每次请求注入 `Authorization: Bearer <token>` |
| `headerPlugin({ name, getValue })` | 每次请求注入自定义 header（值为 null 时跳过） |
| `unwrapPlugin()` | 解包 `{ code, data, message }` 响应；`code !== 200` 时 reject |
| `refreshTokenPlugin({ isLoginUrl?, getRefreshToken, refreshFn, onRefreshFail })` | 401 时自动刷新 token 并重试原请求，刷新失败调用 `onRefreshFail` |

#### `RequestPlugin` 接口

```ts
interface RequestPlugin {
  onRequest?(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>
  onResponse?(response: AxiosResponse): AxiosResponse | Promise<AxiosResponse>
  onResponseError?(error: AxiosError): any
}
```

---

### storage — 本地存储

```ts
import { useStorage, storage } from '@danweiyuan/ekit'
```

#### `useStorage<T>(key: string, defaultValue: T): Ref<T>`

返回响应式 ref，自动同步到 `localStorage`（JSON 序列化，deep watch）。值为 `null`/`undefined` 时自动删除 key。

```ts
const token = useStorage('access_token', '')
token.value = 'abc123' // 自动持久化
```

#### `storage` 对象

非响应式的静态工具：

| 方法 | 签名 | 说明 |
|------|------|------|
| `get` | `<T>(key, defaultValue?) → T \| undefined` | 读取并 JSON.parse，parse 失败返回原始字符串 |
| `set` | `(key, value) → void` | JSON.stringify 后写入 |
| `remove` | `(key) → void` | 删除单个 key |
| `clear` | `() → void` | 清空 localStorage |

---

### date — 日期格式化

```ts
import { formatRelativeTime, formatDate, formatDateTime, formatTime } from '@danweiyuan/ekit'
```

所有函数接受 `string | number | Date`。

| 函数 | 返回示例 | 说明 |
|------|----------|------|
| `formatRelativeTime(d)` | `"刚刚"` / `"5 分钟前"` / `"3 小时前"` / `"2 天前"` / `"2024/1/1"` | 距今相对时间（中文），超过 30 天显示本地化日期 |
| `formatDate(d)` | `"2024-01-15"` | `YYYY-MM-DD` |
| `formatDateTime(d)` | `"2024-01-15 09:30:00"` | `YYYY-MM-DD HH:mm:ss` |
| `formatTime(d)` | `"09:30"` | `HH:mm` |

---

### validators — 表单校验

```ts
import { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from '@danweiyuan/ekit'
```

| 函数 | 签名 | 说明 |
|------|------|------|
| `isPhone(v)` | `(string) → boolean` | 中国大陆手机号（1[3-9]xxxxxxxx） |
| `isEmail(v)` | `(string) → boolean` | 邮箱格式 |
| `isIdCard(v)` | `(string) → boolean` | 18 位居民身份证（末位支持 X/x） |
| `isUrl(v)` | `(string) → boolean` | 有效 URL（基于 `new URL()`） |
| `isRequired(v)` | `(any) → boolean` | 非空：字符串非空白、数组非空、非 null/undefined |
| `minLength(v, min)` | `(string, number) → boolean` | 字符串长度 >= min |
| `maxLength(v, max)` | `(string, number) → boolean` | 字符串长度 <= max |

---

### hooks — Vue Composables

```ts
import { useDebounce, useClickOutside, useEventListener } from '@danweiyuan/ekit'
```

#### `useDebounce<T>(value: Ref<T>, delay?: number): Ref<T>`

返回防抖后的 ref，`delay` 默认 300ms。

```ts
const query = ref('')
const debouncedQuery = useDebounce(query, 500)
watch(debouncedQuery, fetchResults)
```

#### `useClickOutside(target: Ref<HTMLElement | null | undefined>, handler: (e: MouseEvent) => void): void`

监听点击目标元素外部的事件，组件卸载时自动清理。

```ts
const dropdownRef = ref<HTMLElement | null>(null)
useClickOutside(dropdownRef, () => { isOpen.value = false })
```

#### `useEventListener(target, event, handler, options?): void`

绑定事件监听器，组件挂载时注册，卸载时自动移除。`target` 可以是 `EventTarget` 或 `Ref<EventTarget | null | undefined>`。

```ts
useEventListener(window, 'resize', onResize)
useEventListener(buttonRef, 'keydown', onKey, { passive: true })
```
