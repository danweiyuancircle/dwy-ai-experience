# 数据与查询字符串（storage / cookie / date / qs）

> 何时读这份：当用户使用本模块的 API 或问法涉及本模块功能时读取（localStorage 读写、Cookie 读写、日期/时间/时区格式化、查询字符串序列化/解析）。

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
