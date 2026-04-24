<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## request — HTTP 客户端（防腐层）

\`\`\`ts
import {
  createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin,
  SUCCESS_CODE, extractValidationErrors, isApiBusinessError,
} from '@dwydev/ekit'
\`\`\`

### createRequest(options?) → HttpClient

底层是 axios，但**返回 \`HttpClient\` 而不是 \`AxiosInstance\`**。插件按顺序执行请求/响应拦截。

\`\`\`ts
const http = createRequest({
  baseURL: '/api',      // 默认 '/api'
  timeout: 30000,       // 默认 30000
  plugins: [
    tokenPlugin({ getToken: () => localStorage.getItem('token') }),
    unwrapPlugin(),
  ],
})
\`\`\`

### 内置插件

| 插件 | 用途 | 参数 |
|------|------|------|
| tokenPlugin | 自动注入 Bearer token | \`{ getToken: () => string \\| null }\` |
| headerPlugin | 注入自定义请求头 | \`{ name: string, getValue: () => string \\| null }\` |
| unwrapPlugin | 解包 dwyeapi \`{ code, message, data, timestamp }\` 响应，code !== \`"SUCCESS"\` 时 reject | 无参数 |
| refreshTokenPlugin | 401 自动刷新 token 并重试 | \`{ getRefreshToken, refreshFn, onRefreshFail, retry, isLoginUrl? }\` |

### HttpPlugin 接口

\`\`\`ts
interface HttpPlugin {
  onRequest?: (config: HttpConfig) => HttpConfig | Promise<HttpConfig>
  onResponse?: (response: HttpResponse) => HttpResponse | Promise<HttpResponse>
  onResponseError?: (error: HttpError) => any
}
\`\`\`

### dwyeapi 响应契约

后端统一信封 \`{ code, message, data, timestamp }\`，\`code === "SUCCESS"\` 表示业务成功：

\`\`\`json
// 成功响应
{
  "code": "SUCCESS",
  "message": "success",
  "data": { "uuid": "xxx", "name": "Alice" },
  "timestamp": 1713610245
}

// 分页响应（data 为 PageData）
{
  "code": "SUCCESS",
  "message": "success",
  "data": { "items": [...], "total": 150, "page": 1, "page_size": 20 },
  "timestamp": 1713610245
}

// 失败响应
{
  "code": "NOT_FOUND",
  "message": "用户不存在",
  "data": null,
  "timestamp": 1713610245
}
\`\`\`

unwrapPlugin 自动按此契约解包，业务代码拿到的 \`response.data\` 就是纯业务数据或 \`PageData<T>\`：

\`\`\`ts
import type { PageData } from '@dwydev/ekit'

const res = await http.get<User>('/users/1')
// res.data: User

const list = await http.get<PageData<User>>('/users?page=1&page_size=20')
list.data.items       // User[]
list.data.total       // number
list.data.page_size   // number（保持 snake_case 对齐后端）
\`\`\`

### 业务错误分支处理

unwrapPlugin 失败时抛 HttpError，附带 \`businessCode\`（业务错误码）和 \`apiResponse\`（原始信封）：

\`\`\`ts
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
    case 'PERMISSION_DENIED': message.warning('无权限'); break
    case 'VALIDATION_ERROR':
      form.setErrors(extractValidationErrors(err))
      break
    default: message.error(err.message)
  }
}
\`\`\`

### 校验错误回填表单（vee-validate）

\`VALIDATION_ERROR\` 响应的 \`data.errors\` 数组 \`[{ field: "body.email", message: "..." }]\` 可通过 \`extractValidationErrors\` 转为 vee-validate 友好的 \`{ field: message }\` 扁平对象（自动剥离 \`body./query./path./header./cookie.\` 前缀）：

\`\`\`ts
const { handleSubmit, setErrors } = useForm({ validationSchema })

const submit = handleSubmit(async (values) => {
  try {
    await http.post('/users', values)
    message.success('创建成功')
  } catch (err) {
    if (isApiBusinessError(err) && err.businessCode === 'VALIDATION_ERROR') {
      setErrors(extractValidationErrors(err))
    }
  }
})
\`\`\`

### refreshTokenPlugin 详解

\`\`\`ts
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
      retry: (cfg) => http.request(cfg),             // 必填：重放请求
      isLoginUrl: (url) => url.includes('/auth/login'),
    }),
    unwrapPlugin(),
  ],
})
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
