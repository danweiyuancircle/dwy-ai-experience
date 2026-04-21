---
description: Vue 前端网络层(ekit createRequest + 拦截器插件)
paths:
  - "**/api/**/*.ts"
  - "**/api/**/*.vue"
  - "**/api/client.ts"
---

# Vue 前端网络层规范

## 六、API 请求规范

### 强制规则

- API 文件按**业务域拆分**（`api/user.ts`、`api/exam.ts`）
- 每个 API 函数**独立导出**，不使用 default export
- 请求参数和响应使用**类型标注**
- **禁止**在组件中直接创建 axios 实例或调用 `fetch`

### API 文件结构

```typescript
// api/user.ts
import request from '@/utils/request'
import type { UserInfo, UserCreate, UserUpdate } from '@/types/user'

export function getUsers(params?: { page?: number; page_size?: number }) {
  return request.get<{ items: UserInfo[]; total: number }>('/users', { params })
}

export function getUser(id: number) {
  return request.get<UserInfo>(`/users/${id}`)
}

export function createUser(data: UserCreate) {
  return request.post<UserInfo>('/users', data)
}

export function updateUser(id: number, data: UserUpdate) {
  return request.put<UserInfo>(`/users/${id}`, data)
}

export function deleteUser(id: number) {
  return request.delete(`/users/${id}`)
}
```

### 请求实例配置

```typescript
// utils/request.ts
import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Token 注入
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 处理
request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default request
```

### 禁止的写法

```typescript
// ❌ 在组件中直接调用
const res = await axios.get('/api/users')

// ✅ 通过 API 模块调用
import { getUsers } from '@/api/user'
const res = await getUsers()

// ❌ API 函数使用 default export
export default { getUsers, createUser }

// ✅ 每个函数独立导出
export function getUsers() { ... }
export function createUser() { ... }
```

---

## 网络层规范（ekit 统一方案）

### Vue 前端

**唯一方式：** ekit `createRequest()` + 插件。

```typescript
// api/client.ts
import { createRequest } from '@dwydev/ekit'

export const request = createRequest({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  plugins: [
    tokenPlugin(),         // 注入 Authorization header
    refreshTokenPlugin(),  // 401 自动刷新
    unwrapPlugin(),        // 解包响应 → data
  ],
})

// api/user.ts — 按业务域拆分
export function getUsers(params: { page: number; page_size: number }) {
  return request.get('/users', { params })
}

export function createUser(data: UserCreate) {
  return request.post('/users', data)
}
```

**禁止：** `axios.create()`、`fetch()`、`new XMLHttpRequest()`

### 响应解包

前端的解包逻辑必须与后端 eapi response 格式对齐：

```
后端返回: { code: 200, message: "success", data: {...}, timestamp: ... }
                                                  ↓ unwrap
前端拿到: {...}  (直接是 data 的内容)
```

分页响应解包后拿到 `{ items, total, page, page_size }`。
