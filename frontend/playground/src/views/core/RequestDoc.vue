<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## request — Axios 插件化封装

\`\`\`ts
import { createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin } from '@dwydev/ekit'
\`\`\`

### createRequest(options?)

创建带插件系统的 Axios 实例。插件按顺序执行请求/响应拦截。

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
| unwrapPlugin | 解包 \`{ code, data, message }\` 响应，code !== 200 时 reject | 无参数 |
| refreshTokenPlugin | 401 自动刷新 token 并重试 | \`{ getRefreshToken, refreshFn, onRefreshFail, isLoginUrl? }\` |

### RequestPlugin 接口

\`\`\`ts
interface RequestPlugin {
  onRequest?: (config: InternalAxiosRequestConfig) => config | Promise<config>
  onResponse?: (response: AxiosResponse) => response | Promise<response>
  onResponseError?: (error: AxiosError) => any
}
\`\`\`

### refreshTokenPlugin 详解

\`\`\`ts
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
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
