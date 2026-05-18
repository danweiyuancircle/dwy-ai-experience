---
description: Vue 3 + TS + Vite + Tailwind 应用层规范（强制使用 eui/ekit、业务聚合结构、组件 / TS / 路由 / API / 模板 / 样式 / 错误处理 / 注释）
category: Vue
paths:
  - "**/*.vue"
  - "**/*.ts"
  - "**/vite.config.*"
---

# Vue 3 应用层开发规范

适用于基于 Vue 3 + TypeScript + Vite + Tailwind CSS 的前端项目。基础库（组件 / 工具）规范见 `dwy-eui` / `dwy-ekit` skill；状态管理见 `dwy-vue-pinia` rule；测试见 `dwy-vue-testing` rule。

---

## 零、优先使用 eui / ekit 基础库（强制）

`@dwydev/eui` 与 `@dwydev/ekit` 是团队内部 npm 基础库，分别覆盖 UI 组件层与通用工具层。**凡是 eui / ekit 已提供的能力，禁止自行实现，也禁止引入其他库重复造轮子。**

### 必须复用的能力域

| 能力域 | 归属 |
|--------|------|
| 通用 UI 组件（Button / Input / Select / Dialog / Drawer / Form / Table 等） | eui |
| 主题 / 设计 tokens / 暗色模式 | eui |
| 表单校验（vee-validate + zod 集成） | eui + ekit |
| 中后台 / 落地页设计规范 | eui（references） |
| HTTP 客户端（拦截器 / token / 刷新 / 解包） | ekit |
| 本地存储 / Cookie | ekit（storage / cookie） |
| 日期 / 时间格式化 | ekit（date） |
| 数据校验 schema | ekit（validators） |
| PII 数据脱敏 | ekit（masking） |
| 剪贴板 / 文件下载 / qs 序列化 | ekit |
| VueUse 再导出（debounce / throttle / clickOutside / mediaQuery 等） | ekit（hooks） |

### 查阅方式（关键）

**在编写任何 Vue 代码前，以及调用任何 eui / ekit 提供的 API 之前，必须先用 `Skill` 工具加载对应 skill 查阅当前最新接口。** 本文件只规定约束与边界，**不固化**组件 props、函数签名 —— 这些会随版本演进，固化在 rule 里会与实际包不同步。

```
Skill 工具调用：
  - skill="dwy-eui"   组件库 API 与设计规范
  - skill="dwy-ekit"  工具库 API 与契约
```

### 强制规则

- **禁止**业务代码出现 `axios` / `fetch` / `new XMLHttpRequest`，HTTP 走 ekit `createRequest`
- **禁止**直接 `localStorage.getItem` / `setItem` / `removeItem`，走 ekit storage / `useStorage`
- **禁止**直接 `document.cookie` 或单独引入 `js-cookie`，走 ekit cookie
- **禁止**业务代码 `new Date()` / `toLocaleString` / 直接 `import dayjs`，走 ekit date
- **禁止**手写 `navigator.clipboard` / `document.addEventListener('click', ...)` 监听，走 ekit copy / hooks
- **禁止**自定义已有 UI 组件（Button / Input / Select / Dialog / Form / Table 等），走 eui
- **禁止**自定义已有日期 / 时间 / 验证 / 脱敏 / 下载 工具函数，走 ekit
- 涉及任一能力域，**先查 skill 拿到当前 API，再写代码**

---

## 一、项目结构与业务聚合（强制）

### 核心原则

**按功能模块（feature / domain）聚合，禁止按技术层散落。** 同一业务功能的 view / components / store / api / types 必须集中在同一个功能目录下；**禁止**全局存在 `views/` / `components/` / `stores/` / `api/` 等顶级"技术层"目录把不同功能的同类文件混放。

### 为什么

- **跨项目迁移**：复制单个功能目录即可携带该功能全部代码；技术层散落需在 5+ 目录里翻找
- **可读性**：阅读功能时所有相关代码在同一目录，无需跨目录跳转
- **变更影响域清晰**：一次改动 diff 集中，code review 更高效
- **删除友好**：删功能时整个目录删掉即可，不会留下孤儿文件

### 标准结构（参考）

```
src/
├── modules/                    # 业务模块根目录
│   ├── users/                  # 用户功能
│   │   ├── api.ts              # 该业务的 API（用 ekit createRequest 客户端）
│   │   ├── store.ts            # 该业务的 Pinia store
│   │   ├── types.ts            # 该业务的类型
│   │   ├── views/              # 该业务的页面组件
│   │   │   ├── UserListView.vue
│   │   │   └── UserDetailView.vue
│   │   ├── components/         # 该业务的内部组件
│   │   │   └── UserCard.vue
│   │   └── route.ts            # 该业务的路由片段
│   └── orders/
│       ├── api.ts
│       ├── store.ts
│       └── views/
├── shared/                     # 跨业务真正复用：UI 子组件 / composables / 常量
│   ├── components/
│   ├── composables/
│   └── constants/
├── core/                       # 全局基础设施：HTTP client / 路由根 / 主题 / 启动
│   ├── http.ts                 # ekit createRequest 实例（全局唯一）
│   ├── router.ts
│   └── main.ts
├── App.vue
└── style.css
```

> 测试目录与 `src/` 并列、镜像业务聚合结构（详见 `dwy-vue-testing` rule）。

### 强制规则

- **禁止**顶级 `views/` / `components/` / `stores/` / `api/` / `types/` 把不同功能的同类文件混放
- 一个功能目录内文件名固定：`api.ts` / `store.ts` / `types.ts` / `route.ts`（单数、不带功能前缀）
- 跨业务真正共享的代码放 `shared/` 或 `core/`，**禁止**为"可能复用"把单一功能逻辑提前抽离
- 单文件超过约 400 行时再考虑拆分，**禁止**未到规模就预拆分
- 模块间引用通过明确 import，**禁止**循环依赖

## 二、组件规范

### 强制使用 Composition API + `<script setup>`

```vue
<!-- 正例 -->
<script setup lang="ts">
import { ref, computed } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

<!-- 反例：禁止 Options API -->
<script lang="ts">
export default {
  data() { return { count: 0 } },
}
</script>
```

### 组件文件块顺序

```vue
<script setup lang="ts">
// 1. 类型导入
import type { UserInfo } from '@/modules/users/types'

// 2. 组件 / 工具导入
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { EButton, EInput } from '@dwydev/eui'

// 3. Props / Emits
const props = defineProps<{ userId: number; title?: string }>()
const emit = defineEmits<{ submit: [data: UserInfo]; cancel: [] }>()

// 4. Store / Router
const router = useRouter()

// 5. 响应式状态
const loading = ref(false)

// 6. 计算属性
const isValid = computed(() => !!props.title)

// 7. 方法
async function handleSubmit() { /* ... */ }

// 8. 生命周期
onMounted(() => { /* ... */ })
</script>

<template>
  <!-- 模板 -->
</template>
```

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件文件 | `PascalCase.vue` | `UserProfile.vue` |
| 页面组件 | `PascalCase` + View 后缀 | `DashboardView.vue` |
| 组合式函数 | `use` + PascalCase | `useDictionary.ts` |
| Store 文件 | `camelCase.ts` | `auth.ts`、`menu.ts` |
| 类型文件 | `camelCase.ts` | `user.ts` |
| 工具文件 | `camelCase.ts` | `format.ts` |
| 变量 / 函数 | `camelCase` | `userName` / `handleSubmit` |
| 类型 / 接口 | `PascalCase` | `UserInfo` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| 事件处理函数 | `handle` + 动作 | `handleLogin` |
| 布尔变量 | `is/has/can/should` 前缀 | `isLoading` / `hasPermission` |

### 魔法字符串提取常量

同一字符串字面量在文件内出现 ≥ 2 次时，**必须**提取为常量。跨文件复用的 key 放 `shared/constants/`。

### 禁止的写法

- 单字母变量（循环索引除外）
- 不带语义的布尔变量（`const active = ref(true)` → `const isActive = ref(true)`）
- 模板中复杂表达式（提取为 `computed`）

---

## 三、TypeScript 规范

### 强制规则

- 所有 `.ts` / `.vue` 必须用 TypeScript
- **禁止** `any`，除非与外部动态库交互且无法确定类型；使用时必须附中文注释说明原因
- 类型导入用 `import type`
- 联合类型代替 `enum`：`type Status = 'active' | 'inactive'`
- 现代语法：`string[]` 而非 `Array<string>`

### 类型标注

```typescript
// Props 泛型
const props = defineProps<{ title: string; items: UserInfo[] }>()

// Emits 泛型
const emit = defineEmits<{ change: [value: string] }>()

// ref 泛型（复杂类型）
const user = ref<UserInfo | null>(null)
const list = ref<UserInfo[]>([])

// 反例
const user = ref(null)         // 类型推为 Ref<null>
const list = ref([])           // 类型推为 Ref<never[]>
```

### 类型组织

- 跨业务共享类型放 `shared/types/`
- 业务内部类型放该业务的 `types.ts`
- 组件内部一次性类型直接在 `<script setup>` 中声明

---

## 四、路由规范

### 强制规则

- 路由组件**必须** `() => import()` 懒加载
- 认证守卫在 `router.beforeEach`，**禁止**在组件中检查
- meta 字段必须通过 `RouteMeta` 类型扩展声明
- 路径用 **kebab-case**：`/user-profile`，**禁止** `camelCase`

```typescript
// core/router.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/modules/dashboard/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: 'Login' }
  }
})
```

```typescript
// shared/types/router.d.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
    title?: string
  }
}
```

---

## 五、组合式函数（Composables）

- 文件名与函数名以 `use` 开头
- 返回**对象**（非数组），便于解构与按需取

```typescript
export function useList<T>(fetchFn: () => Promise<T[]>) {
  const items = ref<T[]>([])
  const loading = ref(false)
  async function refresh() {
    loading.value = true
    try { items.value = await fetchFn() } finally { loading.value = false }
  }
  onMounted(refresh)
  return { items, loading, refresh }
}
```

通用 hooks（debounce / throttle / clickOutside / mediaQuery 等）**禁止**自己造，走 ekit hooks（具体 API 查 `dwy-ekit` skill）。

---

## 六、API 请求规范

### 强制规则

- HTTP 客户端**必须**用 ekit `createRequest` 创建，全局唯一实例放 `core/http.ts`（具体参数与插件查 `dwy-ekit` skill）
- **禁止**业务代码 `axios.create()` / `fetch()` / `new XMLHttpRequest()`
- 每个业务模块的 API 函数集中在该业务目录的 `api.ts`，按业务域隔离
- 每个 API 函数**独立导出**，**禁止** `default export`
- 请求参数 / 响应**必须**类型标注
- 响应解包契约与 dwyeapi 对齐（`{ code, message, data }`），具体类型与守卫查 `dwy-ekit` skill

### 示例

```typescript
// core/http.ts —— 全局唯一 HTTP 客户端（具体 plugins 查 dwy-ekit skill）
import { createRequest } from '@dwydev/ekit'

export const request = createRequest({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  plugins: [
    /* tokenPlugin / refreshTokenPlugin / unwrapPlugin —— 具体用法查 dwy-ekit skill */
  ],
})

// modules/users/api.ts —— 该业务的 API
import { request } from '@/core/http'
import type { UserInfo, UserCreate } from './types'

export function getUsers(params: { page: number; page_size: number }) {
  return request.get<{ items: UserInfo[]; total: number }>('/users', { params })
}

export function createUser(data: UserCreate) {
  return request.post<UserInfo>('/users', data)
}
```

### 错误处理契约

- 401 / 422 / 业务错误的统一处理由 ekit request 插件完成（具体 API 查 `dwy-ekit` skill）
- 业务侧 catch 用 ekit 提供的 `isApiBusinessError` 类型守卫做分支（`NOT_FOUND` / `VALIDATION_ERROR` / `PERMISSION_DENIED` 等）
- **禁止**每个 API 调用都包 `try/catch`，只在页面级或 store 级统一处理

---

## 七、模板规范

```vue
<!-- v-if / v-for 不在同元素，v-for 必须带 :key -->
<div v-for="item in activeList" :key="item.id">{{ item.name }}</div>

<!-- 事件：方法引用 / 传参用箭头函数 -->
<button @click="handleSubmit">提交</button>
<button @click="() => handleDelete(item.id)">删除</button>

<!-- 组件 PascalCase -->
<UserCard :user="user" @click="handleSelect" />

<!-- 双向绑定优先 v-model -->
<EInput v-model="form.name" placeholder="请输入" />
```

**禁止**：
- `v-if` 与 `v-for` 同元素
- 模板中复杂表达式 / 内联多语句
- `kebab-case` 组件名 / 模板中写 `.value`

---

## 八、样式规范

### 强制使用 Tailwind CSS 4

```vue
<!-- 正例 -->
<div class="flex items-center gap-4 p-6 rounded-lg bg-card">

<!-- 反例 -->
<div style="display: flex; padding: 24px;">
```

### 允许 scoped CSS 的场景

- 第三方 / eui 内部样式覆盖（`:deep(...)`）
- 复杂动画定义
- 无法用 Tailwind 表达的样式

### 响应式与暗色

```vue
<!-- mobile-first -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

<!-- 暗色用 dark: 前缀 -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

---

## 九、Vite 配置

```typescript
// vite.config.ts
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
```

| 规则 | 说明 |
|------|------|
| 路径别名 | 必须配 `@` → `src/` |
| API 代理 | 开发环境必须配 `/api` 代理到后端 |
| 端口 | 默认 5173，可在 `.env` 覆盖 |

---

## 十、错误处理

```typescript
// 异步操作必须有 try / catch 与 loading
async function handleSubmit() {
  loading.value = true
  try {
    await createUser(formData.value)
    message.success('创建成功')
  } catch {
    message.error('创建失败')
  } finally {
    loading.value = false
  }
}
```

- 401 / 422 / 业务错误的拦截走 ekit request 插件（查 `dwy-ekit` skill），**禁止**每个 API 都包 try-catch
- **禁止**空 catch（`try { ... } catch {}` 吞异常）
- 异步操作**必须**有 loading 状态

---

## 十一、环境变量

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=/api
```

| 规则 | 说明 |
|------|------|
| `.env.example` | 必须存在，列出所有变量名 + 注释 |
| `.env` | **禁止**提交 git |
| 命名 | 前端变量必须 `VITE_` 前缀才暴露给客户端 |
| 硬编码 | **禁止**硬编码 API 地址 / 密钥 |

---

## 十二、导入规范

### 顺序（组间空行）

```typescript
// 1. Vue / vue-router 核心
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

// 2. 第三方
import { storeToRefs } from 'pinia'

// 3. @dwydev/* 内部包
import { EButton, EInput } from '@dwydev/eui'
import { request } from '@dwydev/ekit'

// 4. 项目内（@ 别名）
import { useAuthStore } from '@/modules/users/store'
import type { UserInfo } from '@/modules/users/types'
```

### 强制规则

- **必须**用 `@` 别名，**禁止**超过 2 层的相对路径回溯
- 类型用 `import type`，**禁止**与值混合导入

---

## 十三、注释规范

### 强制规则

1. 文件顶部**必须**有中文概述注释，说明文件职责
2. 所有**导出**的方法 / 函数 / 类 / 接口 / 类型**必须**有中文注释
3. 接口字段**必须**逐个 `/** */` 注释
4. 注释说明 **why**（动机 / 边界 / 约束），不复述代码做了什么
5. 全部使用**中文**，**禁止**混用中英文
6. 代码改了，注释**必须**同步更新

### 示例

```typescript
/**
 * 用户基础信息
 */
export interface UserInfo {
  /** 用户 UUID（对外标识，禁止暴露内部自增 id） */
  uuid: string
  /** 用户名（登录账号） */
  username: string
  /** 角色：admin=管理员，user=普通用户 */
  role: 'admin' | 'user'
}

/**
 * 格式化金额显示（输入单位为分，输出元）
 * @param value 金额数值，单位：分
 * @param currency 货币符号，默认 ¥
 */
export function formatMoney(value: number, currency = '¥'): string {
  return `${currency}${(value / 100).toLocaleString()}`
}
```

### 可省略

- 一目了然的 getter / setter
- 测试 `describe` / `it` 块（用例名即描述）
- 组件内部 < 5 行的简单辅助函数

---

## 十四、违规检测清单

AI 编写或审查 Vue 代码时，**必须**检查以下违规模式：

| 严重程度 | 动作 |
|---------|------|
| **致命** | **立即 STOP**，必须修正后才能继续 |
| **高** | 必须修正后才能继续，向用户说明 |
| **中** | 提示风险，建议修正 |

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 未查 skill | 使用 eui / ekit API 前未先查 `dwy-eui` / `dwy-ekit` skill | 高 |
| ekit 重复造轮子 | 自造 HTTP / storage / cookie / date / 校验 / 脱敏 等 ekit 已提供能力 | 高 |
| eui 重复造轮子 | 自造已有 UI 组件（Button / Input / Dialog 等） | 高 |
| 组件直调 axios | 组件内 `axios.get` / `fetch` / `new XMLHttpRequest` | **致命 → STOP** |
| 直接 localStorage | `localStorage.getItem` / `setItem` 出现在业务代码 | 高 |
| 直接 new Date | `new Date()` / `toLocaleString` / 直接 `import dayjs` | 高 |
| 技术层散落 | 顶级 `views/` / `components/` / `stores/` / `api/` 把不同业务混放 | 高 |
| Options API | `<script>` 中 `export default { data, methods, ... }` | **致命 → STOP** |
| Options Store | `defineStore(id, { state, actions })` | **致命 → STOP** |
| any 无注释 | 使用 `any` 但未注释说明原因 | 高 |
| 旧 axios 例子 | 业务里出现 `axios.create()` / `interceptors.request.use(...)` | **致命 → STOP** |
| `v-if` + `v-for` 同元素 | 同一元素既 `v-if` 又 `v-for` | 高 |
| 模板复杂表达式 | 模板中 `.filter(...).length > 0` 等多语句 | 中 |
| 解构 store 丢响应性 | `const { x } = store`（应用 `storeToRefs`） | 高 |
| 注释缺失 | 导出函数 / 类型 / 接口字段无中文注释 | 中 |
| 注释为英文 | 项目中文环境下写英文注释 | 中 |
| 硬编码 API 地址 | URL 直接写在代码里，未走 `import.meta.env` | 高 |
| 相对路径回溯 | `../../../` 跨层导入 | 中 |
| scoped 替代 Tailwind | 大段 scoped CSS 实现可用 Tailwind 表达的样式 | 中 |
| 测试与源码混放 | 测试文件放 `src/` 内（详见 `dwy-vue-testing`） | 高 |
