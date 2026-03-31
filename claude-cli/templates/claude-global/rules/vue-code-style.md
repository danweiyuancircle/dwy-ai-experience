---
paths:
  - "**/*.vue"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/vite.config.*"
  - "**/tsconfig*.json"
---

# Vue 3 + TypeScript + Vite + Pinia 代码规范

所有 Vue / TypeScript 前端项目必须遵循以下规范。AI 生成或修改代码时，必须严格按照这些规则执行。

## 一、项目结构

### 强制规则
- 使用 `pnpm` 作为包管理器
- 使用 `Vite` 作为构建工具
- 必须有 `.node-version` 文件声明 Node 版本
- 必须有 `.npmrc` 配置安装源

### 标准目录结构
```
frontend/
├── src/
│   ├── views/              # 页面组件（一个路由对应一个文件）
│   ├── components/         # 可复用组件
│   ├── stores/             # Pinia 状态管理
│   ├── router/             # Vue Router 配置
│   │   └── index.ts
│   ├── api/                # API 请求模块（按业务域拆分）
│   ├── composables/        # 组合式函数（use* 开头）
│   ├── types/              # 共享类型定义
│   ├── utils/              # 工具函数
│   ├── assets/             # 静态资源
│   ├── App.vue             # 根组件
│   ├── main.ts             # 应用入口
│   └── style.css           # 全局样式（Tailwind 入口）
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
└── .npmrc
```

## 二、组件规范

### 强制使用 Composition API + `<script setup>`

```vue
<!-- ✅ 正确 -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

<!-- ❌ 禁止 Options API -->
<script lang="ts">
export default {
  data() { return { count: 0 } },
  computed: { doubled() { return this.count * 2 } }
}
</script>
```

### 组件文件结构

```vue
<script setup lang="ts">
// 1. 类型导入
import type { UserInfo } from '@/types/user'

// 2. 组件/工具导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 3. Props/Emits 定义
const props = defineProps<{
  userId: number
  title?: string
}>()

const emit = defineEmits<{
  submit: [data: UserInfo]
  cancel: []
}>()

// 4. Store/Router 实例
const router = useRouter()
const authStore = useAuthStore()

// 5. 响应式状态
const loading = ref(false)
const formData = ref<UserInfo | null>(null)

// 6. 计算属性
const isValid = computed(() => !!formData.value?.name)

// 7. 方法
async function handleSubmit() {
  loading.value = true
  try {
    emit('submit', formData.value!)
  } finally {
    loading.value = false
  }
}

// 8. 生命周期
onMounted(() => {
  // ...
})
</script>

<template>
  <!-- 模板 -->
</template>
```

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件文件 | `PascalCase.vue` | `UserProfile.vue`、`LoginView.vue` |
| 页面组件 | `PascalCase` + View 后缀 | `DashboardView.vue`、`LoginView.vue` |
| 组合式函数 | `use` + PascalCase | `useAuth.ts`、`useDictionary.ts` |
| Store 文件 | `camelCase.ts` | `auth.ts`、`menu.ts` |
| API 文件 | `camelCase.ts` | `user.ts`、`exam.ts` |
| 类型文件 | `camelCase.ts` | `user.ts`、`common.ts` |
| 工具文件 | `camelCase.ts` | `request.ts`、`format.ts` |
| 变量/函数 | `camelCase` | `userName`、`handleSubmit` |
| 类型/接口 | `PascalCase` | `UserInfo`、`ExamListParams` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE`、`API_TIMEOUT` |
| 事件处理函数 | `handle` + 动作 | `handleLogin`、`handleDelete` |
| 布尔变量 | `is/has/can/should` 前缀 | `isLoading`、`hasPermission` |

### 禁止的写法

```typescript
// ❌ 单字母变量（循环索引除外）
const d = getData()

// ✅ 有意义的名称
const userData = getData()

// ❌ 不带语义的布尔变量
const active = ref(true)

// ✅ 布尔变量带前缀
const isActive = ref(true)

// ❌ 在模板中使用复杂表达式
<div v-if="list.filter(i => i.status === 'active').length > 0">

// ✅ 用 computed 提取
const hasActiveItems = computed(() => list.value.some(i => i.status === 'active'))
```

## 三、TypeScript 规范

### 强制规则
- 所有 `.ts` 和 `.vue` 文件必须使用 TypeScript
- **禁止**使用 `any`，除非与外部动态库交互且无法确定类型
- 使用 `any` 时必须附注释说明原因
- 类型导入使用 `import type { ... }`

### 类型标注

```typescript
// ✅ Props 使用泛型定义
const props = defineProps<{
  title: string
  count?: number
  items: UserInfo[]
}>()

// ✅ Emits 使用泛型定义
const emit = defineEmits<{
  change: [value: string]
  submit: [data: FormData]
}>()

// ✅ ref 使用泛型
const user = ref<UserInfo | null>(null)
const list = ref<UserInfo[]>([])

// ✅ computed 返回类型由推导，复杂时显式标注
const filters = computed<FilterConfig[]>(() => [...])

// ❌ 不标注类型
const user = ref(null)
const list = ref([])
```

### 类型定义

```typescript
// ✅ 共享类型放 types/ 目录
// types/user.ts
export interface UserInfo {
  id: number
  username: string
  role: 'admin' | 'user'
  email?: string
}

export interface UserCreate {
  username: string
  password: string
  role: 'admin' | 'user'
}

// ✅ 组件内部类型放 script setup 里
interface TableColumn {
  key: string
  label: string
  sortable?: boolean
}
```

### 现代语法（强制）

| 旧写法 | 新写法（强制） |
|--------|--------------|
| `Array<string>` | `string[]` |
| 枚举 `enum Status {}` | 联合类型 `type Status = 'active' \| 'inactive'` |

## 四、Pinia 状态管理

### 强制使用 Setup Store

```typescript
// ✅ Setup Store（强制）
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, login, logout }
})

// ❌ Options Store（禁止）
export const useAuthStore = defineStore('auth', {
  state: () => ({ token: '' }),
  actions: { login() {} }
})
```

### Store 设计原则

| 原则 | 说明 |
|------|------|
| 单一职责 | 一个 store 管理一个业务域（auth、menu、user） |
| 不直接修改 state | 通过方法修改，不在组件中直接 `store.xxx = yyy` |
| 异步操作放 store | API 调用封装在 store 方法中 |
| 解构用 `storeToRefs` | 解构响应式状态必须用 `storeToRefs`，方法直接解构 |

```typescript
// ✅ 正确解构
const store = useReportStore()
const { report, loading } = storeToRefs(store)
const { setReport, reset } = store

// ❌ 错误解构（丢失响应性）
const { report, loading } = store
```

## 五、路由规范

### 强制规则

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})
```

| 规则 | 说明 |
|------|------|
| 懒加载 | 所有路由组件必须使用 `() => import()` 懒加载 |
| 路由守卫 | 认证检查放 `router.beforeEach`，不在组件中检查 |
| meta 类型 | 使用 `RouteMeta` 类型扩展声明 meta 字段 |
| 路径命名 | 使用 kebab-case：`/user-profile`，不用 camelCase |

### 路由守卫

```typescript
// ✅ 全局前置守卫
router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: 'Login' }
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return { name: 'Dashboard' }
  }
})
```

### 路由 Meta 类型声明

```typescript
// types/router.d.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
    title?: string
  }
}
```

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

## 七、组合式函数（Composables）

### 命名规范

- 文件名和函数名必须以 `use` 开头
- 返回值使用对象解构（不使用数组）

```typescript
// composables/useList.ts

// ✅ 正确
export function useList<T>(fetchFn: () => Promise<T[]>) {
  const items = ref<T[]>([])
  const loading = ref(false)

  async function refresh() {
    loading.value = true
    try {
      items.value = await fetchFn()
    } finally {
      loading.value = false
    }
  }

  onMounted(refresh)

  return { items, loading, refresh }
}

// 使用
const { items: users, loading, refresh } = useList(() => getUsers())
```

### 禁止的写法

```typescript
// ❌ 不以 use 开头
export function fetchList() { ... }

// ❌ 返回数组
export function useList() {
  return [items, loading, refresh]
}
```

## 八、模板规范

### 指令使用

```vue
<!-- ✅ v-if/v-else 在同级元素上 -->
<div v-if="isLoading">加载中...</div>
<div v-else>{{ data }}</div>

<!-- ✅ v-for 必须带 key -->
<div v-for="item in list" :key="item.id">{{ item.name }}</div>

<!-- ❌ v-if 和 v-for 在同一元素上 -->
<div v-for="item in list" v-if="item.active" :key="item.id">

<!-- ✅ 用 computed 过滤 -->
<div v-for="item in activeList" :key="item.id">
```

### 事件绑定

```vue
<!-- ✅ 方法引用（无参数时） -->
<button @click="handleSubmit">提交</button>

<!-- ✅ 箭头函数（需要传参时） -->
<button @click="() => handleDelete(item.id)">删除</button>

<!-- ❌ 模板中写复杂逻辑 -->
<button @click="loading = true; api.delete(id).then(() => refresh())">删除</button>
```

### 组件使用

```vue
<!-- ✅ PascalCase 组件名 -->
<UserCard :user="user" @click="handleSelect" />

<!-- ❌ kebab-case 组件名 -->
<user-card :user="user" />

<!-- ✅ 布尔 prop 简写 -->
<EButton loading disabled>提交</EButton>

<!-- ✅ v-model 双向绑定 -->
<EInput v-model="form.name" placeholder="请输入" />
```

## 九、样式规范

### 强制使用 Tailwind CSS

```vue
<!-- ✅ 使用 Tailwind 工具类 -->
<div class="flex items-center gap-4 p-6 rounded-lg bg-card">

<!-- ❌ 使用内联样式 -->
<div style="display: flex; padding: 24px;">

<!-- ❌ 使用 scoped CSS（除非确实需要） -->
<style scoped>
.container { display: flex; }
</style>
```

### 允许 scoped CSS 的场景

- 第三方组件样式覆盖
- 复杂动画定义
- 无法用 Tailwind 实现的样式

```vue
<!-- ✅ 覆盖第三方组件样式时可以用 scoped -->
<style scoped>
:deep(.el-input__inner) {
  border-radius: 8px;
}
</style>
```

### 响应式设计

```vue
<!-- ✅ Mobile-first 响应式 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

<!-- ✅ 暗色模式使用 dark: 前缀 -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

## 十、Vite 配置规范

### 强制配置

```typescript
// vite.config.ts
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

| 规则 | 说明 |
|------|------|
| 路径别名 | 必须配置 `@` → `src/` |
| API 代理 | 开发环境必须配置 `/api` 代理到后端 |
| 端口 | 默认 5173，可在 `.env` 中覆盖 |

## 十一、错误处理

### 强制规则

```typescript
// ✅ 异步操作必须有 try/catch
async function handleSubmit() {
  loading.value = true
  try {
    await createUser(formData.value)
    message.success('创建成功')
    router.push('/users')
  } catch (err) {
    message.error('创建失败')
  } finally {
    loading.value = false
  }
}

// ❌ 没有错误处理
async function handleSubmit() {
  await createUser(formData.value)
  router.push('/users')
}

// ❌ 空 catch
try { ... } catch {}

// ✅ 至少给用户反馈
try { ... } catch { message.error('操作失败') }
```

### Loading 状态

```typescript
// ✅ 所有异步操作必须有 loading 状态
const loading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    data.value = await getData()
  } finally {
    loading.value = false
  }
}
```

## 十二、导入规范

### 导入顺序（按以下顺序排列，组间空行）

```typescript
// 1. Vue 核心
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// 2. 第三方库
import { storeToRefs } from 'pinia'
import axios from 'axios'

// 3. 内部包（@danweiyuan/*）
import { EButton, EInput } from '@danweiyuan/eui'

// 4. 项目内模块
import { useAuthStore } from '@/stores/auth'
import { getUsers } from '@/api/user'
import type { UserInfo } from '@/types/user'
```

### 强制规则

```typescript
// ✅ 使用 @ 别名
import { useAuthStore } from '@/stores/auth'

// ❌ 使用相对路径（超过 2 层）
import { useAuthStore } from '../../../stores/auth'

// ✅ 类型导入使用 import type
import type { UserInfo } from '@/types/user'

// ❌ 类型和值混合导入
import { UserInfo, getUsers } from '@/api/user'
```

## 十三、常见反模式（禁止）

| 反模式 | 正确做法 |
|--------|---------|
| Options API | Composition API + `<script setup>` |
| Pinia Options Store | Setup Store（箭头函数） |
| `this.$refs` | `ref()` + 模板 ref |
| `this.$emit` | `defineEmits<>()` |
| `this.$router` | `useRouter()` |
| `this.$route` | `useRoute()` |
| Vuex | Pinia |
| Mixins | Composables（`use*`） |
| Event Bus | Pinia store 或 `provide/inject` |
| `v-if` + `v-for` 同元素 | computed 过滤后 `v-for` |
| scoped CSS 为主 | Tailwind CSS 为主 |
| 组件中直接调 axios | 通过 `api/` 模块调用 |
| `.value` 在模板中 | 模板自动解包，不需要 `.value` |
| `reactive()` 用于简单值 | `ref()` 用于所有场景 |
| 解构 store 不用 `storeToRefs` | 响应式值必须用 `storeToRefs` |
| 手写 CSS 为主 | Tailwind 工具类为主 |
