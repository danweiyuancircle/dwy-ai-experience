# danweiyuan-eapi 测试用例清单

> 回测基准：48 个测试用例，8 个测试文件。版本变更后必须全部通过。
>
> 运行命令：`cd backend && python -m pytest tests/ -v`

---

## 1. config 模块（7 个）

`tests/test_config.py`

### BaseSettings

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 缺少必填环境变量时抛出 ValueError | 未设置 DATABASE_URL / REDIS_URL / SECRET_KEY 时构造失败 |
| 2 | 设置所有必填字段后正确构造 | database_url、redis_url、secret_key 均正确赋值 |
| 3 | debug 默认值为 False | 未设置 DEBUG 时默认关闭 |
| 4 | allowed_origins 默认为空列表 | 未设置 ALLOWED_ORIGINS 时为 `[]` |
| 5 | 从环境变量解析 allowed_origins | JSON 数组字符串正确解析为 `list[str]` |
| 6 | 子类可扩展自定义字段 | 继承 BaseSettings 后新增字段可从环境变量读取 |
| 7 | JWT 相关字段有合理默认值 | jwt_algorithm 默认 `"HS256"`，access_token_expire_minutes 默认 `30` |

---

## 2. database 模块（3 个）

`tests/test_database.py`

### DatabaseFactory

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 插入并查询记录 | 使用 SQLite 内存库，insert + select 往返一致 |
| 2 | TimestampMixin 包含时间戳列 | FakeModel 具有 `created_at` 和 `updated_at` 属性 |
| 3 | Base 是声明式基类 | Base 拥有 `metadata` 属性且包含已注册表 |

---

## 3. security 模块（9 个）

`tests/test_security.py`

### PasswordHashing（4 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | hash 返回 bcrypt 格式字符串 | 哈希值以 `$2b$` 开头 |
| 2 | 正确密码验证通过 | verify_password 返回 True |
| 3 | 错误密码验证失败 | verify_password 返回 False |
| 4 | 相同密码产生不同哈希 | 两次 hash 结果不相等（盐值随机） |

### JWTTokens（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 5 | 创建并解码 token | payload 中 sub、username 等字段正确还原 |
| 6 | 错误 secret 解码返回 None | 使用不同密钥解码失败，不抛异常 |
| 7 | 过期 token 返回 None | expires_minutes=-1 生成的 token 立即失效 |
| 8 | 无效 token 字符串返回 None | 非 JWT 格式字符串解码返回 None |
| 9 | create_token 不修改输入字典 | 传入的 data dict 在调用后保持不变 |

---

## 4. exceptions 模块（10 个）

`tests/test_exceptions.py`

### AppErrorHierarchy（6 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | AppError 默认 code | code 默认为 `"UNKNOWN_ERROR"` |
| 2 | AppError 自定义 code | 传入 `code="CUSTOM"` 正确赋值 |
| 3 | NotFoundError 格式化消息 | `NotFoundError("用户")` → message 为 `"用户不存在"` |
| 4 | BusinessError 自定义 code 和 message | 正确传递业务错误码和消息 |
| 5 | PermissionDeniedError 默认值 | message `"权限不足"`，code `"PERMISSION_DENIED"` |
| 6 | AuthenticationError 默认值 | message `"认证失败"`，code `"AUTHENTICATION_FAILED"` |

### ExceptionHandlers（4 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 7 | NotFoundError → 404 | 响应体包含 code 和 message |
| 8 | BusinessError → 422 | 响应体包含业务错误码和消息 |
| 9 | PermissionDeniedError → 403 | HTTP 状态码正确映射 |
| 10 | AuthenticationError → 401 | HTTP 状态码正确映射 |

---

## 5. response 模块（6 个）

`tests/test_response.py`

### Success（3 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 默认 message 为 "success" | code=200，包含 timestamp 字段 |
| 2 | 自定义 message | 传入 message="created" 正确覆盖 |
| 3 | data 为 None | 不传 data 时默认 None |

### Fail（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 4 | 默认 code=400，message="fail" | 无参数时使用默认值 |
| 5 | 自定义 code 和 message | 传入 code=500 正确覆盖 |

### Paginated（1 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | 分页响应结构 | data 包含 items、total、page、page_size 四个字段 |

---

## 6. pagination 模块（8 个）

`tests/test_pagination.py`

### paginate（4 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 第 1 页 | offset=0, limit=20 |
| 2 | 第 3 页 | offset=20, limit=10 |
| 3 | page=0 视为第 1 页 | 边界保护，offset 不为负 |
| 4 | page 为负数视为第 1 页 | 边界保护，offset=0 |

### PaginationParams（4 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 5 | 默认值 | page=1, page_size=20 |
| 6 | 自定义值 | page=3, page_size=50 正确赋值 |
| 7 | page 最小值为 1 | page=0 时抛出 ValueError |
| 8 | page_size 最大值为 100 | page_size=101 时抛出 ValueError |

---

## 7. cache 模块（3 个）

`tests/test_cache.py`

### CacheConfiguration

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 未 configure 时 get_redis 抛出 RuntimeError | 错误消息匹配 "not configured" |
| 2 | configure 正确设置 URL | 内部 `_redis_url` 被赋值 |
| 3 | 未连接时 close_redis 安全无异常 | `_redis=None` 时调用不报错 |

---

## 8. dependencies 模块（2 个）

`tests/test_dependencies.py`

### GetDb

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 通过依赖注入创建并查询记录 | POST 创建 → GET 查询，数据一致 |
| 2 | 查询不存在的记录返回 not found | GET 不存在的 ID 返回 `{"error": "not found"}` |

---

## 回测检查清单

```bash
# 1. 全量测试
cd backend && python -m pytest tests/ -v

# 2. 期望结果
# 48 passed

# 3. 单模块测试（调试用）
python -m pytest tests/test_config.py -v
python -m pytest tests/test_database.py -v
python -m pytest tests/test_security.py -v
python -m pytest tests/test_exceptions.py -v
python -m pytest tests/test_response.py -v
python -m pytest tests/test_pagination.py -v
python -m pytest tests/test_cache.py -v
python -m pytest tests/test_dependencies.py -v
```
