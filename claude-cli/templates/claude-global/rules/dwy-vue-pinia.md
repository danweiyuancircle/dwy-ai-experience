---
description: Pinia Setup Store 状态管理规范
paths:
  - "**/stores/**/*.ts"
  - "**/store/**/*.ts"
---

# Pinia 状态管理规范

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

---

## 状态管理规范（跨端共识）

| 平台 | 方案 | 详细规范 |
|------|------|---------|
| Vue | Pinia Setup Store | 见 `dwy-vue-pinia.md`（本文件） |
| Flutter | Riverpod | 见 `flutter-code-style.md` 状态管理章节 |

**跨端共识：**
- 认证状态全局管理（Vue: `useAuthStore`，Flutter: `authProvider`）
- 页面级状态就近管理，不上提到全局
- 缓存策略：列表数据按需刷新，不做客户端持久化缓存（除离线场景）
