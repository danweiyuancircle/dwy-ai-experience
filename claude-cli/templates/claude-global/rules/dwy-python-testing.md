---
description: Python pytest 测试规范
paths:
  - "**/tests/**/*.py"
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/conftest.py"
---

# Python pytest 测试规范

## 十四、测试

### 强制规则
- 使用 `pytest` + `pytest-asyncio` + `httpx`
- 使用 `TestClient` 或 `AsyncClient` 测试 API

```python
# conftest.py
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

# test_user.py
@pytest.mark.anyio
async def test_create_user_returns_201(client: AsyncClient):
    response = await client.post("/users/", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "password" not in data  # 响应不包含密码

@pytest.mark.anyio
async def test_get_nonexistent_user_returns_404(client: AsyncClient):
    response = await client.get("/users/99999")
    assert response.status_code == 404
```

- 测试函数名描述行为而非实现
- 测试数据使用 `pytest.fixture`，不要硬编码
- 测试结构遵循 Arrange-Act-Assert
