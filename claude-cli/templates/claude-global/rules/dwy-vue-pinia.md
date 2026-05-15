---
description: Pinia Setup Store 状态管理规范（强制 Setup Store、storeToRefs、按业务聚合）
paths:
  - "**/store.ts"
  - "**/stores/**/*.ts"
---

# Pinia 状态管理规范

适用于 Vue 3 + Pinia 项目。

---

## 一、强制使用 Setup Store

```typescript
// 正例：Setup Store
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res = await apiLogin({ username, password })
    token.value = res.access_token
  }

  function logout() {
    token.value = null
    user.value = null
  }

  return { token, user, isLoggedIn, login, logout }
})

// 反例：禁止 Options Store
export const useAuthStore = defineStore('auth', {
  state: () => ({ token: '' }),
  actions: { login() {} },
})
```

---

## 二、Store 设计原则

| 原则 | 说明 |
|------|------|
| 单一职责 | 一个 store 管理一个业务域（auth / menu / users），**禁止**把多个业务塞同一个 store |
| 不在组件中直接改 state | 必须通过 store 方法修改，**禁止** `store.xxx = yyy` |
| 异步操作放 store | API 调用封装在 store 方法中，组件不直接调 API（除非纯展示页） |
| 业务聚合 | store 文件放在对应业务模块目录（`modules/users/store.ts`），**禁止**顶级 `stores/` 把不同业务混放 |
| 持久化 | 需要持久化的状态走 ekit storage / `useStorage`（具体 API 查 `dwy-ekit` skill），**禁止**直接 `localStorage` |
| HTTP 调用 | 走全局 ekit `createRequest` 客户端，**禁止**自建 axios 实例 |

---

## 三、storeToRefs 解构

```typescript
import { storeToRefs } from 'pinia'

// 正例：响应式值用 storeToRefs，方法直接解构
const store = useAuthStore()
const { token, user, isLoggedIn } = storeToRefs(store)
const { login, logout } = store

// 反例：直接解构丢失响应性
const { token, user } = store
```

---

## 四、违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| Options Store | `defineStore(id, { state, actions, getters })` | **致命 → STOP** |
| 组件直接改 state | 组件中 `store.xxx = yyy` 直接赋值 | 高 |
| 解构丢响应性 | `const { x } = store` 后在模板里用 `x` | 高 |
| store 跨业务塞功能 | 一个 store 同时管 auth + menu + user 等不相关业务 | 高 |
| 直接 localStorage | store 中直接 `localStorage.setItem(...)`，未走 ekit storage | 高 |
| 自建 HTTP 客户端 | store 中 `axios.create()` / `fetch(...)`，未走 ekit `createRequest` | 高 |
| 顶级 stores 散落 | 顶级 `stores/` 目录把不同业务 store 混放，未按业务聚合 | 高 |
