---
description: 跨栈技术选型强制约束(FastAPI/Vue3/Flutter/UV/pnpm/Docker/S3 等,全局加载)
---

# 跨栈技术选型强制约束

每个领域只有一个方案,AI 不得选替代,不得"建议改用 XX"。

## 后端

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| Web 框架 | FastAPI | Django, Flask, Tornado, Sanic |
| ORM | SQLAlchemy 2.0 (异步) | Tortoise ORM, Peewee, Django ORM |
| 关系数据库 | PostgreSQL | MySQL, MariaDB, SQLite(生产) |
| 缓存 / 消息队列 | Redis | Memcached, RabbitMQ, Kafka |
| 异步任务 | ARQ (eapi[tasks]) | Celery, Dramatiq, Huey |
| 数据库迁移 | Alembic | 手动 DDL, Django migrations |
| 包管理 | UV | pip, Poetry, Pipenv |
| 密码哈希 | bcrypt (eapi security) | argon2, scrypt, 自实现 |
| JWT | python-jose (eapi security) | PyJWT, 自实现 |
| 数据校验 | Pydantic v2 | marshmallow, attrs, 手动校验 |
| 基础设施层 | danweiyuan-eapi | 自造框架、手写基础设施 |
| Linter/Formatter | Ruff | Black, isort, flake8, pylint |

## 前端(Web)

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| 框架 | Vue 3 (Composition API) | React, Svelte, Angular, Vue 2 |
| 构建工具 | Vite | Webpack, Rollup, esbuild 直接用 |
| 组件库 | @danweiyuan/eui | Element Plus, Ant Design Vue, Naive UI |
| 工具库 | @danweiyuan/ekit | 手写 request/storage/validators |
| 状态管理 | Pinia (Setup Store) | Vuex, 手动 reactive/provide |
| 样式 | Tailwind CSS 4 | Sass/Less 手写、CSS Modules、UnoCSS |
| 包管理 | pnpm | npm, yarn |
| 项目结构 | pnpm monorepo (workspace) | Lerna, Nx, Turborepo |
| 表单校验 | vee-validate + zod | 手动 v-model 校验 |
| 路由 | Vue Router 4 | — |
| 测试 | Vitest | Jest |

## 移动端 / 桌面端

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| 框架 | Flutter | React Native, Kotlin Multiplatform, MAUI |
| 状态管理 | Riverpod | GetX, Bloc, Provider, MobX |
| HTTP 客户端 | Dio | http, Chopper, Retrofit |
| 路由 | GoRouter | auto_route, Routemaster |
| 本地存储 | shared_preferences + flutter_secure_storage | Hive, Isar, sqflite(非必要时) |
| 代码生成 | riverpod_generator + freezed + json_serializable | 手写 fromJson/toJson |

## 基础设施

| 领域 | 唯一方案 |
|------|---------|
| 容器化 | Docker + Docker Compose |
| 对象存储(开发) | MinIO (S3 协议) |
| 对象存储(生产) | 任何 S3 兼容云服务 |
| 时序数据库(量化金融) | DolphinDB |
