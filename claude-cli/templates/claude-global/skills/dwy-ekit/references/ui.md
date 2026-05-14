# UI 交互（copy / file / hooks）

> 何时读这份：当用户使用本模块的 API 或问法涉及本模块功能时读取（剪贴板、文件下载/Blob/文件大小、Vue Composables 工具）。

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
