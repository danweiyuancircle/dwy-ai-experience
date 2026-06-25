---
description: 团队内部 dwyeapi 基础框架库强制复用规范（配置 / 异常 / 响应 / 分页 / ORM / 安全 / 缓存 / 时间 / 脱敏 / 日志：禁重复造轮子）
paths:
  - "**/*.py"
---

# Python 后端 dwyeapi 基础库强制复用规范

`dwy-python-backend` rule 的团队内补充。通用 FastAPI / SQLAlchemy / 安全编码规范见 `dwy-python-backend`；本文件只管「凡 dwyeapi 已提供的能力，禁止自行实现，也禁止引入其他库重复造轮子」。

`dwyeapi` 是团队内部 PyPI 基础设施包，已封装后端项目所需的通用能力。

---

## 一、必须复用 dwyeapi 的能力域

| 能力域 | 内容 |
|--------|------|
| 配置管理 | 应用 Settings 基类、运行环境识别（dev / prod） |
| 异常体系 | 业务异常基类与全局异常处理器注册 |
| 统一响应 | `{ code, message, data, timestamp }` 包装 |
| 分页 | 分页查询参数模型与分页响应封装 |
| 数据库 | ORM 声明式基类、时间戳 Mixin、异步引擎与会话工厂 |
| 依赖注入 | FastAPI `get_db` 工厂 |
| 安全 | 密码哈希、JWT 创建与解码 |
| 缓存 | 共享异步 Redis 客户端 |
| 时间 | 业务时间统一入口（Asia/Shanghai） |
| 脱敏 | PII 数据脱敏函数 |
| 日志 | 全局日志配置与门面 |
| 健康检查 | 健康检查路由工厂 |
| 异步任务 | 耗时任务队列与上下文 |
| 邮件 | 邮件验证码可插拔通道 |

### 查阅方式（关键）

**在编写任何后端代码前，以及调用任何 dwyeapi 提供的 API 之前，必须先用 `Skill` 工具加载 `dwy-eapi` skill 查阅当前最新接口。** 本文件**只规定约束与边界**，**不固化** dwyeapi 的具体模块路径、类名、函数签名、参数 —— 这些会随版本演进，固化在 rules 里会与实际包不同步。

```
Skill 工具调用：skill="dwy-eapi"
```

---

## 二、强制规则

- 涉及上表任一能力域，**先查 skill 拿到当前 API，再写代码**
- **禁止**自造异常基类，必须复用 dwyeapi 异常体系
- **禁止**手写 bcrypt / PyJWT 调用，必须走 dwyeapi 安全模块
- **禁止**自定义统一响应包装函数，必须用 dwyeapi 响应模块
- **禁止**自定义分页模型，必须用 dwyeapi 分页模块
- **禁止**自定义 `DeclarativeBase`，模型必须继承 dwyeapi 提供的基类
- **禁止**在路由函数中直接创建数据库会话，必须用 dwyeapi 依赖工厂
- **禁止**自建 Redis 连接池，必须用 dwyeapi 共享客户端
- **禁止**在业务代码中直接使用 `datetime.now()`，必须用 dwyeapi 时间模块
- **禁止**自行 `logging.basicConfig`，必须用 dwyeapi 日志模块

---

## 三、各能力域 dwyeapi 落点

通用规范（路由 / Schema / ORM / 安全编码本身的要求）见 `dwy-python-backend` 对应章节；本节只说明这些规范在团队项目里**必须落到哪个 dwyeapi 模块**。

| 能力 | 团队项目落点 | 对应通用规范 |
|------|-------------|-------------|
| 统一响应 / 异常 | dwyeapi 响应模块 + 异常体系（禁自造） | backend 二、五 |
| 分页 | dwyeapi 分页模块（禁自定义） | backend 二 |
| ORM 基类 / 时间戳 | 继承 dwyeapi 声明式基类与 Mixin | backend 六 |
| `get_db` 依赖 | dwyeapi 依赖工厂 | backend 四 |
| 密码哈希 | dwyeapi 安全模块（bcrypt，禁手写） | backend 7.2 |
| JWT 创建 / 解码 | dwyeapi 安全模块（禁直接 PyJWT） | backend 7.3 |
| PII 脱敏 | dwyeapi 脱敏函数 | backend 7.4 |
| 审计日志 | dwyeapi 日志模块获取审计 logger | backend 7.8 |
| 业务时间 | dwyeapi 时间模块（禁裸 `datetime.now()`） | backend 六 / 七 |
| Redis 缓存 | dwyeapi 共享客户端（禁自建连接池） | backend 八 |

> 密码复杂度校验建议下沉到 dwyeapi 提供统一的 `PasswordStr` 类型，避免每个项目重复实现。

---

## 四、违规检测清单（dwyeapi 相关）

通用后端违规清单见 `dwy-python-backend` 第十节；涉及 dwyeapi 必须额外检查：

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 重复造轮子 | 自造异常基类 / 自封装统一响应 / 手写 bcrypt 或 JWT 调用 / 自建 Redis 连接池 等 dwyeapi 已提供能力 | 高 |
| 未查 skill | 调用 dwyeapi 能力域却未先查 `dwy-eapi` skill 拿当前 API | 高 |
| 密码弱存储 | 使用 MD5 / SHA 而非 dwyeapi 安全模块的 bcrypt | **致命 → STOP** |
| `datetime.now()` 直用 | 业务代码直接 `datetime.now()` 而非走 dwyeapi 时间模块 | 高 |
