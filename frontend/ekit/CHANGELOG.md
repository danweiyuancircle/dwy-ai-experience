# @dwydev/ekit

## 0.4.0

### Minor Changes

- 包名从 `@danweiyuan/ekit` 迁移至 `@dwydev/ekit`，下游需更新 import 路径和 package.json 依赖
- 同步更新全局规则、CLI 模板、playground 文档中的包名引用

## 0.2.1

### Patch Changes

- 修复类型导出：types 从源码 .ts 改为编译后的 .d.ts，消费者不再需要安装 @types/js-cookie、@types/file-saver、@types/qs
- 修复 CookieAttributes 类型导入方式（命名空间导出）
- 新增 vite.config.ts 构建配置，使用 vite-plugin-dts 生成声明文件

## 0.2.0

### Minor Changes — 基于开源库扩展 7 个模块

**重构模块：**

- **date** — 用 dayjs 重构，新增 `formatBy()` 自定义格式 + 导出配置好的 `dayjs` 实例（zh-cn locale + relativeTime 插件）
- **validators** — 用 zod 重构，新增 7 个 zod schema 导出（`phoneSchema`、`emailSchema`、`idCardSchema`、`urlSchema`、`requiredSchema`、`minLengthSchema`、`maxLengthSchema`）

**新增模块：**

- **copy** — `copyText()` + `useClipboard()` composable（浏览器 Clipboard API）
- **cookie** — `useCookie()` composable + `cookie` 对象（基于 js-cookie）
- **qs** — `stringify()` + `parse()`（基于 qs 库，默认 arrayFormat: repeat）
- **file** — `downloadFile()` + `saveBlob()` + `formatFileSize()`（基于 file-saver + axios 集成）
- **hooks/vueuse** — 从 @vueuse/core 精选 re-export：`useThrottle`、`useWindowSize`、`useMediaQuery`、`useIntersectionObserver`、`useResizeObserver`

**新增依赖：**

| 库 | 版本 | 用途 |
|----|------|------|
| dayjs | ^1.11.20 | 日期处理 |
| zod | ^3.25.76 | 表单校验 schema |
| js-cookie | ^3.0.5 | Cookie 管理 |
| qs | ^6.15.0 | URL query string |
| file-saver | ^2.0.5 | 文件下载保存 |
| @vueuse/core | ^14.2.1 | Vue composable 工具集 |

139 个测试全部通过。

## 0.1.0

首次发布。从 `@danweiyuan/core` 重命名而来，统一 "e = easy" 命名体系。

### 模块

- **request** — Axios 插件化封装 `createRequest()`，内置 token/header/unwrap/refreshToken 插件
- **storage** — `useStorage()` composable + 静态 `storage` 对象（localStorage 响应式封装）
- **date** — `formatRelativeTime`、`formatDate`、`formatDateTime`、`formatTime`
- **validators** — `isPhone`、`isEmail`、`isIdCard`、`isUrl`、`isRequired`、`minLength`、`maxLength`
- **hooks** — `useDebounce`、`useClickOutside`、`useEventListener`
