# @danweiyuan/ekit

## 0.1.0

首次发布。从 `@danweiyuan/core` 重命名而来，统一 "e = easy" 命名体系。

### 模块

- **request** — Axios 插件化封装 `createRequest()`，内置 token/header/unwrap/refreshToken 插件
- **storage** — `useStorage()` composable + 静态 `storage` 对象（localStorage 响应式封装）
- **date** — `formatRelativeTime`、`formatDate`、`formatDateTime`、`formatTime`
- **validators** — `isPhone`、`isEmail`、`isIdCard`、`isUrl`、`isRequired`、`minLength`、`maxLength`
- **hooks** — `useDebounce`、`useClickOutside`、`useEventListener`
