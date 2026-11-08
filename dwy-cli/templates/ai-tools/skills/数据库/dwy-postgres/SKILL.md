---
name: dwy-postgres
description: 设计、修改或排查 PostgreSQL 数据库、连接、权限与敏感数据时使用。
---

# PostgreSQL 开发

先核实实际 PostgreSQL 版本、连接方式、用户权限、数据规模和项目已有迁移机制。按任务读 [PostgreSQL 规范](references/dwy-postgres.md)；数据库连接与凭据从环境或配置获取，不写入代码、日志或示例。涉及数据变更先评估兼容性与回滚，破坏性操作遵循已有授权边界。

历史资料提到的 `dwy-db-migration` 对应 `dwy-alembic`；只有项目使用 Alembic 时才适用。
