# dwy-auth

## 0.1.0

- 首次通过 GitHub Actions OIDC 发布到公开 PyPI，导入命名空间为 `dwy_auth`。
- 提供独立 `AuthRuntime`、身份提供方合同与可替换 `SessionBackend`；应用持有用户模型、数据库会话和迁移，核心不依赖 EAPI 或 FastAPI。
- 支持 Google 身份、可选邮箱密码认证、令牌轮换、设备撤销与账户删除；配置、邮件发送器和存储资源由宿主注入。
- 保留需要 EAPI 的服务、HTTP 路由与管理员 Cookie 兼容接口；通过 `dwyeapi[auth]==0.12.0` 安装配套集成。
