---
description: Alembic 数据库迁移规范
paths:
  - "**/alembic/**"
  - "**/alembic.ini"
  - "**/migrations/**"
---

# Alembic 数据库迁移规范

## 一、初始化

```bash
cd backend
alembic init alembic
```

## 二、配置

```python
# alembic/env.py — 必须配置项
from app.database import Base        # 导入 ORM Base
from app.models import *             # 导入所有模型(确保被扫描到)
target_metadata = Base.metadata
```

## 三、工作流

```bash
# 模型变更后生成迁移
alembic revision --autogenerate -m "add user table"

# 执行迁移(dev 和 prod 相同)
alembic upgrade head

# 回滚一步
alembic downgrade -1
```

## 四、强制规则

- 每次 model 变更**必须**生成 migration 文件,禁止手动 `CREATE TABLE`
- 迁移文件**必须**提交到 git,dev 和 prod 共用同一套迁移
- 生产数据库只通过 `alembic upgrade head` 变更 schema
- 迁移文件命名:Alembic 自动生成 revision ID + 人类可读描述
- 禁止在迁移文件中写业务数据操作(seed data 放 scripts/ 目录)
