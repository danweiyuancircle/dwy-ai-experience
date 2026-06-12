# @dwydev/ekit

## 0.9.1

### Patch Changes

- 增加 GitHub Actions OIDC 发布链路测试版本，支持通过 `@dwydev/ekit@x.y.z` tag 自动发布到 npm，并同步创建 GitHub Release。

## 0.8.0

### Minor Changes

- **新增 `useFormPersist` composable**：让表单字段在页面刷新后自动从 sessionStorage 回填，提升填写中途意外刷新的体验。内置敏感字段排除清单（password / code / token / secret 等共 18 项，不区分大小写），调用方可通过 `exclude` 选项追加项目自定义字段；支持 `storage: 'local' | 'session'` 切换持久介质；返回 `{ form, reset, clear }`，提交成功后调 `reset()` 清空残留。导出 `DEFAULT_SENSITIVE_FIELDS` 常量与 `UseFormPersistOptions` / `UseFormPersistReturn` 类型

## 0.7.1

### Patch Changes

- `unwrapPlugin` 补齐 `onResponseError` 钩子,从 `error.response.data` 提取 `code`/`message` 挂到 `HttpError` 上。修复 dwyeapi 业务错走 4xx(典型如 `EMAIL_EXISTS=422`、`VALIDATION_ERROR=422`、`INVALID_EMAIL_CODE=422`)时,axios 走 onResponseError 路径导致 `businessCode` 不被设置,业务 catch 拿不到错误码无法分支的问题。配套 3 个新增回归测试。

## 0.7.0

### Breaking Changes

- `unwrapPlugin` 成功判定从 `code === 200`（数字）改为 `code === "SUCCESS"`（字符串），对齐 dwyeapi v0.7.0 响应信封。升级后必须同步后端至 `dwyeapi ≥ 0.7.0`

### Minor Changes

- 新增 dwyeapi 响应契约类型：`ApiResponse<T>` / `PageData<T>` / `ValidationErrorData` / `ValidationFieldError` / `CommonBusinessCode` / `BusinessCode`
- 新增 `SUCCESS_CODE` 常量导出
- 新增响应错误辅助工具：`extractValidationErrors`（自动剥离 `body./query./path./header./cookie.` 前缀，与 vee-validate `setErrors` 兼容）、`isApiBusinessError` 类型守卫、`ApiBusinessError` 类型
- `HttpError` 新增可选字段 `businessCode`（业务错误码）和 `apiResponse`（原始信封），unwrapPlugin 失败时自动附加，业务可按 `err.businessCode` 分支处理
- `refreshTokenPlugin` 消息提取优先级调整为 `message → detail → error.message`（优先 dwyeapi 的 `message`，兼容 FastAPI 默认 `detail`），并在 reject 时透传 `businessCode` / `apiResponse`

### Docs

- `SKILL.md` / `README.md` / playground `RequestDoc.vue` 同步到新契约，补齐业务错误码表和 vee-validate 回填示例

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
