---
description: PostgreSQL 安全与配置规范（参数化查询、应用用户最小权限、连接池上限、SSL、敏感字段加密）
---

# PostgreSQL 安全与配置规范

适用于使用 PostgreSQL 作为主数据库的 Python 后端项目。

---

## 一、强制规则

| 规则 | 说明 |
|------|------|
| 参数化查询 | **禁止**字符串拼接 SQL（用 ORM 或 `text(... :param)` 参数绑定） |
| 应用用户权限 | 只授予 SELECT / INSERT / UPDATE / DELETE，**不给** DROP / CREATE / ALTER / SUPERUSER |
| 端口暴露 | **禁止**将 `5432` 直接暴露到公网；仅允许 VPC / 内网 / 跳板机访问 |
| 运行权限 | PostgreSQL 服务进程**禁止**以 `root` 用户运行，必须使用专用低权限系统用户 |
| 连接池 | `pool_size ≤ 20`，`max_overflow ≤ 10` |
| SSL 连接 | 生产环境启用 `sslmode=require` |
| 敏感字段加密 | 身份证号 / 银行卡 / 手机号原文等使用 AES 加密**存储**，不仅展示脱敏 |
| 迁移 | 通过 Alembic 管理 schema，**禁止**手动执行 DDL（详见 `dwy-db-migration` rule） |

---

## 二、应用专用数据库用户（最小权限）

生产环境**禁止**使用 `postgres` 超级用户跑应用；为每个应用创建独立用户，授权严格限定到 DML。

数据库服务自身也**禁止**由 `root` 直接启动或托管，统一使用 `postgres` 或发行版默认专用系统账号运行。

```sql
-- 创建应用专用用户（非超级用户）
CREATE USER app_user WITH PASSWORD 'strong_password';

-- 库与 schema 访问
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- 现有对象权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 默认权限（迁移新增表自动生效）
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO app_user;
```

### 禁止授予应用用户的权限

- `GRANT ALL PRIVILEGES`
- `SUPERUSER`
- `CREATEDB` / `CREATEROLE`
- 任何能修改 schema 的权限（DROP / CREATE / ALTER）

> 迁移操作使用单独的 migrator 账号（具备 DDL 权限），与应用账号严格区分。

---

## 三、连接串与 SSL

- 连接串必须从环境变量读取，**禁止**硬编码
- 生产环境必须 `sslmode=require`（或更严的 `verify-full`）
- 连接池参数走 dwyeapi 引擎工厂（具体 API 查 `dwy-eapi` skill），**禁止**手动 `create_async_engine` 跳过框架约束

---

## 四、敏感字段加密

仅展示脱敏（详见 `dwy-python-backend` 7.4 响应安全）**不足以**保护落库数据。以下字段在写入前必须用 AES 加密：

- 身份证号
- 银行卡号
- 手机号（视业务敏感等级）
- 真实姓名 + 地址组合（PII）

加密密钥从环境变量或 KMS 读取，**禁止**与库一起备份。

---

## 五、违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| SQL 拼接 | f-string / `%` / 字符串相加构造 SQL | **致命 → STOP** |
| 应用用户超权 | 应用账号拥有 DROP / CREATE / ALTER / SUPERUSER | **致命 → STOP** |
| 超级用户跑应用 | 应用以 `postgres` 或其他超级用户身份连接 | **致命 → STOP** |
| 公网开放 5432 | 安全组 / 防火墙 / LB 允许公网直连 PostgreSQL 端口 | **致命 → STOP** |
| root 运行数据库 | PostgreSQL 服务进程以 `root` 身份运行 | **致命 → STOP** |
| 连接池超限 | `pool_size > 20` 或 `max_overflow > 10` | 高 |
| 无 SSL | 生产环境连接串无 `sslmode=require` | 高 |
| 敏感字段明文 | 身份证 / 银行卡等明文落库 | 高 |
| 硬编码连接串 | 连接串写死在代码中 | **致命 → STOP** |
