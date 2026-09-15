---
description: Python 后端四层分包与依赖方向（Assembly / Features / BizFoundation / Foundation）；uv workspace 根锁定第三方版本
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python 四层架构与依赖

适用于 uv workspace 的 Python 后端。路由 / Schema / ORM / 安全编码见 `dwy-python-backend`。本文件只管**层、引用边、版本写在哪**。

单壳项目**不建** PlatformFoundation。

---

## 一、层名（冻结）

正式层名只有下表四个。目录 / 包可以叫 `app`、`biz_foundation`，文档可写「本仓包名 X = Foundation」。**禁止**把 `Domain` / `infra` / `core` 当层名。

| 层 | 判定（只用这一条） | 禁止 |
|---|---|---|
| **Foundation** | 换一个完全不同的产品仍原样拿走 | 出现本业务名词 |
| **BizFoundation** | 本产品才有，但跨多个 Feature 都要用 | 页面、导航、某一端壳状态 |
| **Features** | 可整包删/裁剪的业务域 | 被其他 Feature 直接引用 |
| **Assembly** | 生命周期、DI、路由挂载、把实现插进 Protocol | 业务规则、业务计算 |

升层：第二个 Feature 或第二个产品**真在用**，才升到 BizFoundation / Foundation。禁止「可能复用」提前抽。

业务内聚：一个业务域 = `features/` 下的一个包。域内 `router.py` / `service.py` / `schemas.py` / `models.py` 聚在一起。禁止全局 `routers/` `services/` `models/`。

---

## 二、依赖边（强制）

```
app → features/* → biz_foundation → foundation
         ✕ 互引
```

| 谁 | 允许依赖 | 禁止 |
|---|---|---|
| `app/` | `features/*`、`biz_foundation`、`foundation`（仅 factories） | 业务计算 |
| `features/orders` | 仅 `biz_foundation` | `app`、`features/inventory`、`foundation` |
| `biz_foundation` | 仅 `foundation` | `app`、任何 Feature |
| `foundation` | 第三方库 | 任何本仓业务包 |

**Feature 互引为零。** 跨域只许三种：升到 `biz_foundation`；Feature 只依赖 Protocol，由 `app/factories.py` / `app/hooks.py` 注入实现；`app` 编排两次调用。

依赖倒置原则：Feature 依赖 Protocol，不依赖 Doris/Http 具体类。具体实现只出现在 `app/`。

声明与源码两道都查：

- `features/orders/pyproject.toml` 的 `dependencies` 只许出现 `biz_foundation` 与无版本第三方名
- 源码禁止 `from app.`、`from features.inventory`、`from foundation.`

```python
# 合法：只认抽象，实现由装配层注入
class StockPort(Protocol):
    """扣库存端口。orders 不 import inventory 包。"""

    async def deduct(self, sku: str, qty: int) -> None: ...


class OrderService:
    """下单。stock 由 app/factories.py 注入。"""

    def __init__(self, stock: StockPort) -> None:
        self._stock = stock
```

```python
# 禁止
from app.main import settings                    # Feature → Assembly
from features.inventory.service import deduct    # Feature → Feature
from foundation.db import get_session            # Feature 越层
```

---

## 三、分包树

打开 `backend/` 必须能数出四层。业务词只出现在 `features/` 下。

```
backend/
  app/                            # Assembly
    main.py                       # 注册 router、lifespan
    factories.py                  # 唯一实例化具体实现的地方
    hooks.py                      # 跨 Feature 桥
  features/                       # Features
    orders/
      pyproject.toml
      src/orders/
        router.py
        service.py
        schemas.py
        models.py
    inventory/
      pyproject.toml
      src/inventory/
        router.py
        service.py
        schemas.py
        models.py
  biz_foundation/                 # BizFoundation
    pyproject.toml
    src/biz_foundation/
      auth/                       # 内容：跨 Feature 鉴权，不是一层
      protocols.py
  foundation/                     # Foundation
    pyproject.toml
    src/foundation/
      db.py
      redis.py
      signing.py
  pyproject.toml                  # workspace + 第三方版本只在这
  uv.lock
```

```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = ["features/*", "biz_foundation", "foundation"]
```

`app/` 是根应用，不是 workspace member。测试镜像层：`tests/features/orders/`、`tests/biz_foundation/`。

---

## 四、Monorepo 版本（强制）

第三方版本号**只**出现在仓库根 `pyproject.toml` 的 `constraint-dependencies`。成员包只写包名。内部包用 uv workspace，不写版本。一把锁：根 `uv.lock`。选哪个版本走 `dwy-dependency-freshness`。

```toml
# 根 pyproject.toml
[tool.uv.sources]
biz_foundation = { workspace = true }
foundation = { workspace = true }

[tool.uv]
constraint-dependencies = [
  "fastapi==0.115.6",
  "sqlalchemy==2.0.36",
]
```

```toml
# features/orders/pyproject.toml
[project]
dependencies = [
  "fastapi",           # 无版本
  "biz_foundation",
]
```

禁止成员 `pyproject.toml` 写 `fastapi==0.115.6`。禁止每个包自己 `uv lock`。

---

## 五、检查清单

| 检查项 | 严重 |
|---|---|
| 顶层不是 `app` / `features` / `biz_foundation` / `foundation` 四层 | 高 |
| Feature `from app.` 或 pyproject 依赖 `app` | 高 |
| Feature import 另一 Feature | 高 |
| Feature 源码 `from foundation.` | 高 |
| 成员包写死第三方版本 | 高 |
| `Domain` / `infra` / `core` 当层名 | 中 |
