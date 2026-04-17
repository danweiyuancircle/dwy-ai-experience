---
description: 后端/前端/Flutter/Monorepo 项目目录结构模板(按项目入口文件触发)
paths:
  - "**/package.json"
  - "**/pyproject.toml"
  - "**/pubspec.yaml"
  - "**/pnpm-workspace.yaml"
---

# 项目目录结构模板

AI 创建文件时**必须**遵循以下目录结构,不得自造目录名或层级。

---

## 一、后端项目(FastAPI)

```
backend/
├── src/app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口 + lifespan
│   ├── config.py             # 继承 eapi BaseSettings
│   ├── database.py           # create_async_engine_factory + create_session_factory
│   ├── dependencies.py       # FastAPI Depends(get_db, get_current_user)
│   ├── exceptions.py         # 项目级异常(继承 eapi AppError)
│   ├── validators.py         # 输入校验工具(防注入等)
│   ├── models/               # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py           # 每个实体一个文件
│   │   └── ...
│   ├── schemas/              # Pydantic v2 请求/响应模型
│   │   ├── __init__.py
│   │   ├── user.py           # UserCreate, UserUpdate, UserResponse
│   │   └── ...
│   ├── routers/              # FastAPI 路由(按业务域拆分)
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证端点
│   │   ├── user.py           # 每个业务域一个文件
│   │   └── ...
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py           # 与 router 同名,一一对应
│   │   └── ...
│   ├── tasks.py              # ARQ 任务注册(@register 装饰器)
│   └── worker.py             # ARQ Worker 入口
├── alembic/                  # 数据库迁移
│   ├── versions/             # 迁移文件
│   ├── env.py
│   └── alembic.ini
├── scripts/                  # 初始化/运维脚本
│   ├── init_db.py            # 初始化数据库表结构
│   └── seed_admin.py         # 创建初始管理员
├── tests/
│   ├── conftest.py           # pytest fixtures(SQLite 内存库、mock)
│   ├── test_auth.py          # 与 routers/ 同名
│   └── ...
├── pyproject.toml            # UV 依赖配置
├── Dockerfile.dev            # 开发容器(--reload)
├── Dockerfile.prod           # 生产容器(只读、non-root)
├── .env.example              # 环境变量模板
└── TEST_CASES.md             # 测试用例清单
```

**强制规则:**
- 分层:`routers → schemas → services → models → database`,不可跨层调用
- services 层抛 eapi 异常(AppError 子类),**不抛 HTTPException**
- routers 层只做参数接收和 response 包装,**不写业务逻辑**
- models/ schemas/ routers/ services/ 四个目录内文件按业务域一一对应

---

## 二、前端项目(Vue 3)

```
frontend/
├── src/
│   ├── main.ts               # createApp + 插件注册
│   ├── App.vue               # 根组件
│   ├── router/
│   │   └── index.ts          # Vue Router 配置 + 守卫
│   ├── stores/               # Pinia Setup Store
│   │   ├── auth.ts           # 认证状态
│   │   └── ...
│   ├── api/                  # HTTP 客户端(按业务域拆分)
│   │   ├── client.ts         # ekit createRequest() 实例
│   │   ├── auth.ts           # 登录/注册接口
│   │   ├── user.ts           # 用户接口
│   │   └── ...
│   ├── views/                # 页面级组件(路由对应)
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   └── ...
│   ├── components/           # 共享 UI 组件(非页面级)
│   ├── composables/          # Vue 3 组合式函数(use* 前缀)
│   ├── utils/                # 纯工具函数
│   └── index.css             # Tailwind CSS 入口
├── tests/
│   ├── api/
│   ├── stores/
│   ├── router/
│   └── utils/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile                # 生产构建(多阶段)
└── TEST_CASES.md
```

**强制规则:**
- views/ 放页面组件(路由直接引用),components/ 放复用组件
- api/ 每个文件对应后端一个 router 模块,保持命名一致
- stores/ 统一 Setup Store 写法(`export const useXxxStore = defineStore('xxx', () => {...})`)

---

## 三、Flutter 项目

```
lib/
├── main.dart                  # runApp + ProviderScope
├── app.dart                   # MaterialApp.router + GoRouter
├── core/
│   ├── config/
│   │   └── env.dart           # 环境配置
│   ├── network/
│   │   ├── dio_client.dart    # Dio 实例 + 拦截器
│   │   └── api_response.dart  # 统一响应模型(对齐 eapi 格式)
│   ├── storage/
│   │   └── secure_storage.dart
│   ├── theme/
│   │   └── app_theme.dart     # ThemeData + 设计 tokens
│   └── utils/
├── features/                  # 按功能模块拆分(feature-first)
│   └── {feature_name}/
│       ├── data/
│       │   ├── {feature}_repository.dart   # Repository 实现
│       │   └── {feature}_dto.dart          # 数据传输对象
│       ├── domain/
│       │   └── {feature}_entity.dart       # 领域实体
│       └── presentation/
│           ├── {feature}_page.dart         # 页面
│           ├── {feature}_provider.dart     # Riverpod Provider
│           └── widgets/                    # 功能内专属 Widget
├── shared/
│   ├── providers/             # 全局 Provider(auth, theme)
│   ├── widgets/               # 跨功能共享 Widget
│   └── models/                # 共享数据模型
test/
├── features/
│   └── {feature_name}/
└── core/
```

**强制规则:**
- features/ 按功能模块拆分,每个模块自包含 data/domain/presentation
- core/ 放全局基础设施(网络、存储、主题),不放业务代码
- shared/ 放跨功能共享的 provider/widget/model

---

## 四、Monorepo 项目结构(pnpm workspace)

当项目包含前端 + 后端时,使用 monorepo:

```
project-root/
├── backend/                   # FastAPI 后端(上述第一节结构)
├── frontend/                  # Vue 前端(上述第二节结构)
├── mobile/                    # Flutter 移动端(上述第三节结构,独立管理)
├── docker-compose.dev.yml     # 开发环境
├── docker-compose.prod.yml    # 生产环境
├── dev.sh                     # 一键启动脚本
├── pnpm-workspace.yaml        # pnpm monorepo 配置
├── package.json               # 根 package.json(scripts)
├── CLAUDE.md                  # 项目规范
└── .env.example               # 全局环境变量模板
```

**注意:** Flutter 项目(mobile/)不纳入 pnpm workspace,独立用 `flutter pub get` 管理依赖。
