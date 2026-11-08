---
name: dwy-alembic
description: 创建、审查或排查使用 Alembic 的 SQLAlchemy 数据库结构迁移时使用。
---

# Alembic 迁移

先检查项目现有 Alembic 配置、元数据、迁移历史与目标数据库，避免重建已初始化的环境。按任务读 [Alembic 迁移](references/dwy-db-migration.md)；示例导入路径需按当前项目替换。自动生成后人工检查升级、回滚和现有数据兼容性；生产执行与破坏性变更按用户授权及项目流程处理。
