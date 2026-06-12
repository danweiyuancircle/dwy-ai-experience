---
description: Python pytest 测试规范（目录组织、fixture、异步、AAA 结构）
paths:
  - "**/tests/**/*.py"
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/conftest.py"
---

# Python pytest 测试规范

## 一、测试目录组织（强制）

### 核心约束

**测试目录与业务源码并列、独立存放。** 测试文件**禁止**混入源码目录（`src/` 或 `app/` 等）。

### 强制规则

- 测试目录与源码目录平级、独立，常用名 `tests/`（也可按团队约定，但**必须**独立）
- **禁止**在源码目录中放任何 `test_*.py` / `*_test.py` 文件
- 测试目录内部结构应**镜像**对应源码结构，便于定位被测对象
- 测试文件命名：`test_{被测模块名}.py`（pytest 默认发现规则）
- 测试函数命名：`test_{被测行为}` —— 描述行为而非实现
- 全局 fixture 放测试根目录的 `conftest.py`，子目录 fixture 放对应子目录的 `conftest.py`
- pytest 配置在 `pyproject.toml` 显式声明：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

- 测试依赖（`pytest` / `pytest-asyncio` / `httpx` / `pytest-mock` 等）放 `[dev]` 或 `[test]` extras，**禁止**进生产依赖
- 跨包发布的代码不得 import 测试目录下的内容

> 具体目录布局由项目结构决定（单包、monorepo 子包、扁平 `app/` 等），AI 自行判断；唯一不变的是"测试目录独立、与源码并列"。

### 标准目录结构(仅供参考)

```
project/
├── src/
│   └── app/
│       ├── routers/
│       │   └── user.py
│       ├── services/
│       │   └── user.py
│       ├── models/
│       │   └── user.py
│       └── main.py
├── tests/                          # 测试根目录
│   ├── conftest.py                 # 全局 fixture（client / db_session 等）
│   ├── routers/
│   │   ├── __init__.py
│   │   └── test_user.py            # 测 app/routers/user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── test_user.py            # 测 app/services/user.py
│   └── models/
│       ├── __init__.py
│       └── test_user.py            # 测 app/models/user.py
└── pyproject.toml
```

---

## 二、技术栈

- 使用 `pytest` + `pytest-asyncio` + `httpx`
- API 测试使用 `httpx.AsyncClient` 配合 `ASGITransport`，**禁止**使用同步 `TestClient` 测异步路由

---

## 三、Fixture

### 强制规则

- 测试数据使用 `pytest.fixture`，**禁止**在测试函数中硬编码业务数据
- 数据库相关 fixture 必须保证测试间隔离（每个测试事务回滚或重建表）
- 跨测试共享的 fixture 放 `conftest.py`，单文件用的 fixture 留在文件内

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
```

---

## 四、测试编写规范

### 强制规则

- 测试结构遵循 **Arrange-Act-Assert**（准备 → 调用 → 断言）
- 一个测试只验证一个行为，**禁止**在一个 test 函数中堆多个不相关断言
- 断言要具体（断言字段值），**禁止**只断言"不报错"
- 必须覆盖：成功路径、失败路径（404 / 422 / 401 / 403）、边界值
- 敏感字段（密码、token）**必须**显式断言**不在**响应中

```python
# tests/routers/test_user.py
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_user_returns_201_without_password(client: AsyncClient):
    # Arrange
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepass123",
    }

    # Act
    response = await client.post("/users/", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "password" not in data
    assert "hashed_password" not in data

@pytest.mark.anyio
async def test_get_nonexistent_user_returns_404(client: AsyncClient):
    response = await client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
```

---

## 五、违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 测试与源码混放 | 测试文件放在 `src/` 或 `app/` 内（如 `app/services/test_user.py`） | 高 |
| 测试目录不规范 | 项目无 `tests/` 目录或 `pyproject.toml` 未配 `testpaths` | 高 |
| 镜像结构断裂 | 测试目录结构与源码目录结构不对应，难以定位 | 中 |
| 同步 TestClient | 异步路由用同步 `TestClient` 测试 | 高 |
| 测试无断言 | 只调用接口不断言响应字段 | 高 |
| 敏感字段未校验 | 用户接口测试未断言密码字段不在响应中 | 高 |
| 测试数据硬编码 | 复用的测试数据不抽 fixture，散落在多个 test 函数中 | 中 |
| 测试依赖泄漏 | `pytest` 等测试依赖进入生产依赖列表 | 高 |
