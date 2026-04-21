---
description: Vue 3 + TS + Vite + Tailwind 基础风格(组件/TS/模板/样式/反模式/错误处理)
paths:
  - "**/*.vue"
  - "**/vite.config.*"
---

# Vue 3 基础风格规范

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
├── tests/                  # 测试文件（独立目录，禁止放在 src/ 内）
│   ├── utils/              # 对应 src/utils/
│   ├── stores/             # 对应 src/stores/
│   ├── api/                # 对应 src/api/
│   ├── router/             # 对应 src/router/
│   └── components/         # 对应 src/components/
├── index.html
├── package.json
├── vite.config.ts
├── vitest.config.ts        # 测试配置（独立文件）
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

### 禁止魔法字符串

同一个字符串字面量在文件内出现 2 次及以上时，**必须**提取为常量。

```typescript
// ❌ 魔法字符串散落多处，改一处漏一处
storage.set('access_token', token)
// ...
const t = storage.get('access_token')

// ✅ 提取为常量
const ACCESS_TOKEN_KEY = 'access_token'
storage.set(ACCESS_TOKEN_KEY, token)
const t = storage.get(ACCESS_TOKEN_KEY)

// ❌ 事件名、路由路径、storage key 等重复字面量
emit('update:modelValue', value)
router.push('/dashboard')
localStorage.getItem('theme')

// ✅ 跨文件共享的 key 放到专门的常量文件
// constants/storage-keys.ts
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  THEME: 'theme',
} as const
```

**判断标准：** 同一字符串在同一文件出现 ≥ 2 次 → 提取为常量。跨文件使用的 key → 提取到 `constants/` 目录共享。

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

// 3. 内部包（@dwydev/*）
import { EButton, EInput } from '@dwydev/eui'

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

## 十三、注释规范

### 强制规则

所有 `.ts` 和 `.vue` 文件必须遵循以下注释规则：

1. **文件顶部必须有概述注释** — 说明文件的功能和职责
2. **所有导出的方法/函数必须有中文注释** — 说明用途、参数、返回值
3. **所有导出的类必须有中文注释** — 说明类的职责
4. **所有导出的接口/类型必须有中文注释** — 说明类型含义，每个字段也需注释
5. **复杂的内部方法必须有中文注释** — 简单的 getter/setter 可省略
6. **注释使用中文** — 与代码保持一致的语言风格

### 文件顶部注释

```typescript
/**
 * 用户认证相关的 API 请求模块
 * 提供登录、登出、刷新 token、获取用户信息等接口
 */
import { request } from '@/utils/request'
import type { LoginParams, UserInfo } from '@/types/user'
```

```vue
<!--
  用户信息卡片组件
  展示用户头像、昵称、角色标签，支持点击跳转到用户详情页
-->
<script setup lang="ts">
// ...
</script>
```

### 方法/函数注释

```typescript
/**
 * 用户登录
 * @param params 登录参数（用户名、密码）
 * @returns 登录成功后返回用户信息和 token
 */
export async function login(params: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', params)
}

/**
 * 格式化金额显示
 * @param value 金额数值（单位：分）
 * @param currency 货币符号，默认 ¥
 * @returns 格式化后的金额字符串，如 ¥1,234.56
 */
export function formatMoney(value: number, currency = '¥'): string {
  return `${currency}${(value / 100).toLocaleString()}`
}
```

### 类注释

```typescript
/**
 * HTTP 请求客户端
 * 封装 axios，提供拦截器、错误处理、token 自动刷新等能力
 */
export class RequestClient {
  // ...
}
```

### 接口/类型注释

```typescript
/**
 * 用户基础信息
 */
export interface UserInfo {
  /** 用户 ID */
  id: number
  /** 用户名（登录账号） */
  username: string
  /** 用户角色：admin=管理员，user=普通用户 */
  role: 'admin' | 'user'
  /** 邮箱地址（可选） */
  email?: string
}

/**
 * 分页查询参数
 */
export interface PageParams {
  /** 当前页码，从 1 开始 */
  page: number
  /** 每页条数，默认 20 */
  pageSize: number
}
```

### 组件 Props/Emits 注释

```vue
<script setup lang="ts">
/**
 * 数据表格组件的 Props 定义
 */
interface Props {
  /** 表格数据源 */
  data: Record<string, unknown>[]
  /** 列配置 */
  columns: TableColumn[]
  /** 是否显示加载中 */
  loading?: boolean
}

const props = defineProps<Props>()

/**
 * 组件事件定义
 */
const emit = defineEmits<{
  /** 行点击事件，参数为当前行数据 */
  rowClick: [row: Record<string, unknown>]
  /** 选中行变化事件，参数为选中的行数组 */
  selectionChange: [rows: Record<string, unknown>[]]
}>()
</script>
```

### 组合式函数注释

```typescript
/**
 * 列表数据管理 composable
 * 封装列表加载、刷新、loading 状态
 * @param fetchFn 数据获取函数
 * @returns 列表数据、加载状态、刷新方法
 */
export function useList<T>(fetchFn: () => Promise<T[]>) {
  // ...
}
```

### 可省略注释的场景

- 一目了然的 getter/setter（如 `get name() { return this._name }`）
- 测试文件中的 `describe` / `it` 块（用例名本身就是描述）
- 组件内部的简单辅助函数（< 5 行且逻辑清晰）
- 私有变量的简单赋值

### 禁止的写法

```typescript
// ❌ 无文件头注释
import { ref } from 'vue'
export function login() { ... }

// ❌ 方法无注释
export async function deleteUser(id: number) {
  return request.delete(`/users/${id}`)
}

// ❌ 接口字段无说明
export interface UserInfo {
  id: number
  username: string
  role: 'admin' | 'user'
}

// ❌ 英文注释（与代码风格不一致）
/** Get user info by id */
export async function getUser(id: number) { ... }

// ❌ 废话注释（只复述代码，不说明 why）
/** 设置 count 为 0 */
count.value = 0
```

### 注释质量要求

| 要求 | 说明 |
|------|------|
| 说明 why 而非 what | 代码已经说明 what，注释要解释为什么这样写 |
| 语言一致性 | 全部使用中文，不混用中英文 |
| 描述业务含义 | 避免"获取数据"这种泛泛说法，要写"获取用户列表" |
| 标注边界条件 | 参数范围、特殊取值、空值处理要说明 |
| 及时更新 | 代码修改后必须同步更新注释，禁止留下过时注释 |

## 十四、常见反模式（禁止）

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
| 测试文件放在 `src/` 内 | 放在独立 `tests/` 目录 |
| 测试中用相对路径回溯 `../../src/` | 用 `@` 别名导入 |

## 十五、代码简约原则

### 核心思想

代码只写**必要的逻辑**，不写"以防万一"的冗余代码。信任 TypeScript 类型系统和框架保证，只在系统边界（用户输入、外部 API）做校验。

### 禁止的冗余模式

```typescript
// ❌ 不必要的 fallback — 类型已保证
const name = props.title ?? ''       // props.title 声明为 string，不可能是 null
const items = data.value || []       // ref<Item[]>([]) 初始就是数组

// ✅ 直接使用
const name = props.title
const items = data.value

// ❌ 不必要的可选链 — 值一定存在
const id = user?.id                  // user 来自必传 prop，不可能是 undefined

// ✅ 直接访问
const id = user.id

// ❌ 不必要的条件渲染守卫
<div v-if="list">                    // list 是 ref<Item[]>([])，永远为真值
  <div v-for="item in list" ...>

// ✅ 直接渲染
<div v-for="item in list" ...>

// ❌ 不必要的空函数 fallback
const onClick = props.onSubmit ?? (() => {})

// ✅ 条件调用
props.onSubmit?.()

// ❌ 不必要的 try-catch 吞异常
try {
  await api.getUsers()
} catch {
  // 空 catch，bug 永远不会被发现
}

// ✅ 让异常暴露或给用户反馈
try {
  await api.getUsers()
} catch {
  toast.error('加载失败')
}
```

### 判断标准

写每一行防御代码前问自己：**这个情况在当前上下文下真的会发生吗？**

- 如果**会** → 写防御，加注释说明触发条件
- 如果**不会** → 不写，信任上游保证
- 如果**不确定** → 查看类型定义和调用链确认，不要"以防万一"

## 代码自检（写代码时强制执行）

**每次生成或修改 Vue/TypeScript 代码后，必须逐条验证以下清单。任何一条未通过 → STOP，立即修正后再继续。**

| # | 检查项 | 违规即 STOP |
|---|--------|------------|
| 1 | 使用 `<script setup lang="ts">`，不是 Options API | ✓ |
| 2 | Props 用 `defineProps<{}>()`，Emits 用 `defineEmits<{}>()` | ✓ |
| 3 | 无 `any` 类型（除非有注释说明原因） | ✓ |
| 4 | `ref()` 复杂类型有泛型标注（`ref<T>` 而非 `ref(null)`） | ✓ |
| 5 | Pinia 使用 Setup Store，不是 Options Store | ✓ |
| 6 | Store 解构用 `storeToRefs`（响应式值），方法直接解构 | ✓ |
| 7 | 类型导入用 `import type { ... }` | ✓ |
| 8 | 路由组件使用 `() => import()` 懒加载 | ✓ |
| 9 | API 调用通过 `api/` 模块，未在组件中直接 `axios.get` | ✓ |
| 10 | 布尔变量有 `is/has/can/should` 前缀 | ✓ |
| 11 | 样式以 Tailwind 为主，非必要不写 scoped CSS | ✓ |
| 12 | 无 `v-if` + `v-for` 同元素 | ✓ |
| 13 | 模板无复杂表达式，已提取为 `computed` | ✓ |
| 14 | 枚举用联合类型 `type X = 'a' | 'b'`，不用 `enum` | ✓ |
| 15 | 测试文件在 `tests/` 目录，不在 `src/` 内 | ✓ |
| 16 | `tsconfig.app.json` 的 include 不包含 `tests/` | ✓ |
| 17 | 文件顶部有中文概述注释，说明文件职责 | ✓ |
| 18 | 所有导出的方法/函数有中文注释（含参数、返回值） | ✓ |
| 19 | 所有导出的类/接口/类型有中文注释，接口字段逐个注释 | ✓ |
| 20 | Props/Emits 定义有中文注释说明每个字段/事件 | ✓ |

**不执行自检就提交代码 = 违规。**

---

## 错误处理（跨栈约束）

### 前端（Vue）

通过 ekit request 插件统一处理：

```typescript
// 在 api/client.ts 配置拦截器后，业务代码不需要 try/catch
// 401 → refreshToken 插件自动刷新，失败则跳登录
// 422 → unwrap 插件抛出错误，页面级 catch 显示 message
// 其他错误 → 全局错误提示
```

**禁止：** 每个 API 调用都包 try/catch，应在页面级或 store 级统一处理。

---

## 环境变量管理

### 前端（Vite）

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=/api
```

代码中通过 `import.meta.env.VITE_API_BASE_URL` 访问。**只有 `VITE_` 前缀的变量会暴露给客户端。**

### 强制规则

| 规则 | 说明 |
|------|------|
| 每个项目必须有 `.env.example` | 列出所有变量名 + 注释说明，值用占位符 |
| `.env` 文件禁止提交 git | 已在 git-security.md 约束 |
| 禁止硬编码 | 数据库连接、密钥、API 地址等必须走环境变量 |
| 禁止运行时读取 `.env` 文件 | 后端用 BaseSettings（启动时加载），前端用 Vite 编译注入 |
