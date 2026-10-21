# 管理员 Web 认证迁移

`modules/auth/web` 提供私有 `@dwydev/auth-web@0.1.0`，迁入管理员登录组件、Cookie API 和内存会话。品牌、可信首页/登录路径、回跳参数与同源 backend 根地址由宿主注入。未迁入业务导航、用户/交易/配置页面；Google-only 应用用户与管理员 Cookie 保持不同会话，没有新增 Google Web、邮箱验证码或业务 App 登录 UI。

## 来源

来源为独立 app-cloud 仓库；迁移前备份标识 `$SOURCE_BACKUP/app-cloud-source.tar.gz`，以下 SHA256 针对归档内原始文件 bytes：

| app-cloud 仓库相对路径 | SHA256 |
| --- | --- |
| `frontend/src/features/auth/LoginPage.vue` | `a5221c0fdfa90fcaedebad95ac062f10b398c6e04df52f9456c3f82afdb76c26` |
| `frontend/src/shared/api.ts` | `598ef26e75406fa4115932a3c758cd9e6045078671a87d44a1076cece233d7f7` |
| `frontend/src/shared/session.ts` | `f435c928636ae889cb3ee37fe35c42f9f8d4ea0a65b4972e5ae4db7c0a6260b6` |

提取保留 EUI 表单和用户名/密码输入上界；共享 API 使用标准 fetch，强制同源 Cookie、禁止重定向、禁止缓存，拒绝跨源 backend。相比原宿主，增加双入口输入校验、安全身份响应投影、只读内存身份及会话失效后迟到响应保护。

## 宿主改动

以下均为 app-cloud 仓库相对路径：

- `frontend/src/features/auth/LoginPage.vue`：保留业务路由入口，改为品牌/路由注入薄封装。
- `frontend/src/shared/session.ts`：创建共享认证 API/会话；部署地址来自 `VITE_ADMIN_API_BASE_URL`，缺省 `/api/admin`，只允许同源。
- `frontend/src/shared/api.ts`：认证三方法委托共享会话；所有业务查询仍在宿主，原 ekit 业务 API 和 401 事件保留。
- `frontend/src/shared/types.ts`：管理员身份类型从共享库重导出。
- `frontend/src/router.ts`、`frontend/src/main.ts`、`frontend/src/App.vue`：分别改为 restore、invalidate 与服务端成功后退出，避免直接写只读身份。
- `frontend/src/style.css`：增加共享组件 Tailwind source。
- `frontend/package.json`、`frontend/pnpm-lock.yaml`：接入本地共享包的临时相对 `file:` 依赖，用于迁移验证；发布后须切换为固定私有 Release tgz 并重新锁定。
- `frontend/tests/workspaces.test.ts`、`frontend/tests/TEST_CASES.md`：身份准备改为 HTTP mock 后 restore，保留原业务断言。

没有编辑宿主其他业务页面，也没有更改后端、账户数据或数据库配置。

## 实际验证

- 先写 3 个测试文件，确认因缺失实现而失败，再实现；`pnpm --dir modules/auth/web test`：3 suites / 25 tests 通过。
- `pnpm --dir modules/auth/web build`：通过，含 TypeScript declarations。
- app-cloud `frontend` 的 `pnpm test`：最终完整运行 21 suites / 82 tests 通过。首次运行暴露旧测试直接写只读身份，改为走 restore 后完成最终完整回归。
- app-cloud `frontend` 的 `pnpm build`：完整 `vue-tsc --noEmit && vite build` 通过。
- `pnpm --dir modules/auth/web pack --pack-destination .artifacts`：真实生成 `modules/auth/web/.artifacts/dwydev-auth-web-0.1.0.tgz`；8 个归档文件，没有测试、源码目录、source map、node_modules 或环境文件。该次 SHA256：`088df87dc499a631020523bebb9ee7375eaf406d7529238ed7ede0e93c52bd8e`。
- `node modules/auth/web/scripts/smoke-pack.mjs`：重新打真实 tgz，在全新临时消费目录 `pnpm install`，从安装包导入 API/会话/组件，执行 mock HTTP 登录退出、内存身份断言及真实 EUI/Vue SSR；输出 `fresh tgz consumer: API + memory session + Vue component SSR passed`。消费验证未引用 workspace 源文件；EUI/Vue/lucide 使用其固定历史版本 peers。临时目录运行后清理。
- 本机 Node 26 单测局部设置 `NODE_OPTIONS=--no-experimental-webstorage`，避免实验性全局 localStorage 覆盖 jsdom；CI 仍使用 Node 22.14。

## 边界与后续

网络边界已 mock；以上不声称完成真实浏览器 Cookie/SameSite/CSRF、线上管理员登录或 Google OAuth 验收。后端负责 Cookie 属性与同源请求校验。没有执行公共/私有发布、提交或推送；根任务负责独立 review、实际私有 Release、下载产物哈希校验，以及宿主从临时 file 依赖切换固定私有 tgz 的最终安装回归。
