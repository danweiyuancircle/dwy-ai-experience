# request — HTTP 客户端（防腐层）

> 何时读这份：当用户使用本模块的 API 或问法涉及本模块功能时读取（HTTP 请求、createRequest、内置插件、refreshToken、dwyeapi 响应契约对接、业务错误捕获）。

```ts
import {
  createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin,
  SUCCESS_CODE, extractValidationErrors, isApiBusinessError,
} from '@dwydev/ekit'
import type {
  HttpClient, HttpConfig, HttpResponse, HttpError, HttpPlugin,
  HttpMethod, HttpResponseType, CreateRequestOptions,
  ApiResponse, PageData, ValidationErrorData, ValidationFieldError,
  CommonBusinessCode, BusinessCode, ApiBusinessError,
} from '@dwydev/ekit'
```

## createRequest(options?) → HttpClient

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

## HttpConfig / HttpResponse / HttpError

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
  businessCode?: string                  // v0.7.0 新增：后端业务错误码（如 "NOT_FOUND"）
  apiResponse?: ApiResponse<unknown>     // v0.7.0 新增：原始 dwyeapi 响应信封
}
```

## HttpPlugin 接口

```ts
interface HttpPlugin {
  onRequest?: (config: HttpConfig) => HttpConfig | Promise<HttpConfig>
  onResponse?: (response: HttpResponse) => HttpResponse | Promise<HttpResponse>
  // 返回非 undefined 视为已恢复，终止后续插件
  onResponseError?: (error: HttpError) => any
}
```

> 旧版的 `RequestPlugin` 已重命名为 `HttpPlugin`，所有钩子参数类型从 axios 类型改为 ekit 自有契约。

## 内置插件

| 插件 | 用途 | 参数 |
|------|------|------|
| `tokenPlugin` | 注入 `Authorization: Bearer <token>` | `{ getToken: () => string \| null }` |
| `headerPlugin` | 注入自定义动态 header | `{ name: string, getValue: () => string \| null }` |
| `unwrapPlugin` | 解包 dwyeapi `{ code, message, data, timestamp }`，code !== `"SUCCESS"` 时 reject（附带 `businessCode` / `apiResponse`）；非该格式原样透传 | 无 |
| `refreshTokenPlugin` | 401 自动刷新并重放 | 见下 |

## refreshTokenPlugin（带 retry 注入）

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

## 响应契约对齐 dwyeapi v0.7.0

所有接口统一信封 `{ code, message, data, timestamp }`，`code === "SUCCESS"` 表示业务成功。unwrapPlugin 自动按此契约解包，业务代码拿到的 `response.data` 就是纯业务数据或 `PageData<T>`。

```ts
import { SUCCESS_CODE } from '@dwydev/ekit'
import type { ApiResponse, PageData } from '@dwydev/ekit'

// 单体响应
const res = await http.get<User>('/users/1')
// res.data: User（unwrap 后是 User 不是 ApiResponse<User>）

// 分页响应
const list = await http.get<PageData<User>>('/users?page=1&page_size=20')
list.data.items          // User[]
list.data.total          // number
list.data.page           // number
list.data.page_size      // number（保持 snake_case 对齐后端 JSON）
```

**内置业务错误码（`CommonBusinessCode`）：**

| code | HTTP | 含义 |
|------|------|------|
| `SUCCESS` | 200 | 业务成功，unwrap 自动解包 data |
| `NOT_FOUND` | 404 | 资源不存在 |
| `BUSINESS_ERROR` | 422 | 业务规则不允许（基础码；业务常自定义为 `INSUFFICIENT_BALANCE` 等） |
| `PERMISSION_DENIED` | 403 | 无权限 |
| `AUTHENTICATION_FAILED` | 401 | 认证失败 |
| `VALIDATION_ERROR` | 422 | 请求参数校验失败，`data.errors` 为字段错误数组 |
| `INTERNAL_ERROR` | 500 | 服务器错误 |
| `HTTP_{status_code}` | 原状态 | 第三方 HTTPException 透传（如 OAuth2 的 `HTTP_401`） |

`BusinessCode = CommonBusinessCode | (string & {})`：既自动补全常见码，又允许业务 `BusinessError(code="CUSTOM")` 自定义。

## 捕获业务错误：isApiBusinessError + extractValidationErrors

unwrapPlugin 失败时抛 `HttpError`，附带 `businessCode`（业务错误码）和 `apiResponse`（原始信封）。业务 catch 直接按 code 分支：

```ts
import { isApiBusinessError, extractValidationErrors } from '@dwydev/ekit'

try {
  await http.post('/orders', body)
} catch (err) {
  if (!isApiBusinessError(err)) {
    message.error('网络异常')
    return
  }
  switch (err.businessCode) {
    case 'INSUFFICIENT_BALANCE': showRecharge(); break
    case 'NOT_FOUND': message.warning('订单不存在'); break
    case 'VALIDATION_ERROR':
      // err.apiResponse.data.errors: [{ field: "body.email", message: "..." }, ...]
      form.setErrors(extractValidationErrors(err))
      break
    default: message.error(err.message)
  }
}
```

`extractValidationErrors` 自动剥离 `body. / query. / path. / header. / cookie.` 前缀，返回 `{ field: message }` 扁平对象，与 vee-validate 的 `form.setErrors` 直接兼容。嵌套字段路径（如 `body.items.0.name`）保留为 `items.0.name`。输入可以是 HttpError、完整 ApiResponse、或裸 `ValidationErrorData`，非校验错误时返回空对象。
