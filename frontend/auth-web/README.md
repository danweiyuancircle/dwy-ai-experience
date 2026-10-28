# @dwydev/auth-web

管理员的 Vue 3 登录表单、同源 Cookie API 和内存会话。Google-only 应用用户认证由独立后端/Apple 模块处理；本包没有 Google Web、邮箱验证码、业务用户登录、业务导航或管理数据页面。

源码仓库公开，安装包通过 `.github/workflows/publish-auth-web.yml` 发布到公开 npm；发布后可使用 `pnpm add @dwydev/auth-web` 安装，无需源码仓库权限。

```ts
import { createAdminAuthApi, createAdminSession } from '@dwydev/auth-web'

const session = createAdminSession(createAdminAuthApi({
  baseURL: '/api/admin',
  onSessionExpired: () => session.invalidate(),
}))
await session.restore() // 新页面会话必须由服务器校验 Cookie
```

在宿主 `EConfigProvider` 内使用 `AdminLogin`，传入 `auth={ login: session.login }`、品牌 `brand`、固定可信的 `homePath`/`loginPath`，以及可选的不可信 `redirect`、`initialError`。监听 `authenticated(identity, path)` 后由宿主路由跳转。`redirect` 只允许站内路径，拒绝协议相对 URL、反斜线、控制字符和歧义的编码分隔符。宿主必须处理导航失败。

`createAdminAuthApi` 只接受同源根地址（例如 `/api/admin`），跨源后端须由宿主反向代理。三个端点为 `POST /auth/login`、`GET /auth/me`、`POST /auth/logout`；成功响应为 `{ code: 'SUCCESS', data }`，身份数据只保留 `username`。POST 登录 body 为 `{ username, password }`。用户名去首尾空格后为 1–64 字符，密码为 1–256 字符；不以客户端校验替代后端校验。HTTP/业务/格式/网络错误均 reject；`AdminAuthError.response.status` 提供 HTTP 状态。

请求使用 `credentials: 'same-origin'`、`mode: 'same-origin'`、`redirect: 'error'`、`cache: 'no-store'` 和 15 秒超时。浏览器管理 HttpOnly Cookie；本包不读写 Cookie、localStorage/sessionStorage 或 Bearer token。需要支持标准 fetch 与 `AbortSignal.timeout` 的浏览器。Cookie 的 Secure/SameSite/CSRF 检查仍由后端负责。

`createAdminSession` 每次调用返回独立实例，`administrator` 为只读 Vue ref；`login`、`restore` 在成功时更新安全身份，失败清空身份；`logout` 在服务端撤销成功后清空，失败保留重试入口。`invalidate` 处理业务 API 的 401，并使此前在途响应失效。身份仅用于显示，所有授权仍由服务端确认。

宿主已有 Vue/EUI/lucide peers，不新增运行时依赖。宿主加载 EUI theme 与 Tailwind，并增加：

```css
@source "../node_modules/@dwydev/auth-web/dist/**/*.js";
```

从仓库根运行：

```sh
pnpm --dir frontend/auth-web test
pnpm --dir frontend/auth-web build
pnpm --dir frontend/auth-web pack
node frontend/auth-web/scripts/smoke-pack.mjs
```

Node 26 的实验性全局 localStorage 会覆盖 jsdom，可仅在本地单测命令前设置 `NODE_OPTIONS=--no-experimental-webstorage`；CI 使用仓库固定 Node 22.14。测试清单见 `frontend/auth-web/tests/TEST_CASES.md`。
