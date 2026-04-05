# danweiyuan-eapi 测试用例清单

> 回测基准：90 个测试用例，9 个测试文件。版本变更后必须全部通过。
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

## 9. tasks 模块（42 个）

`tests/test_tasks.py`

### TaskModel（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | Task 自动生成 ID | id 以 `task_` 开头，长度 37 |
| 2 | 默认状态为 PENDING | 新建 Task status = "pending" |
| 3 | 默认进度为 0 | 新建 Task progress = 0 |
| 4 | 默认 result 为 None | 新建 Task result is None |
| 5 | params 作为 JSON 存储 | dict 存入后正确取出 |

### TaskStatus（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | 状态枚举值 | pending/running/success/failed/canceled 均存在 |
| 7 | StrEnum 兼容字符串 | 可用于 f-string 拼接 |

### Schemas（3 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | TaskCreate 校验有效输入 | task_type 和 params 正确赋值 |
| 9 | TaskResponse 从 ORM 对象构造 | model_validate 成功，字段映射正确 |
| 10 | TaskListResponse 结构 | items 列表 + total 计数 |

### Service — create_task（3 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 11 | 创建任务返回带 ID 的 Task | id 以 `task_` 开头，status = PENDING |
| 12 | 创建的任务持久化到数据库 | 可通过 select 查到 |
| 13 | 创建的任务有初始日志 | logs 包含"任务已创建" |

### Service — get_task（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 14 | 查询已存在的任务 | 返回正确的 Task 对象 |
| 15 | 查询不存在的任务返回 None | 未找到时返回 None |

### Service — list_tasks（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 16 | 空列表 | 无任务时返回 ([], 0) |
| 17 | 返回所有任务 | 3 个任务全部返回 |
| 18 | 分页 | page=1, page_size=2 返回 2 条，total=5 |
| 19 | 按 status 筛选 | 只返回 RUNNING 状态的任务 |
| 20 | 按 task_type 筛选 | 只返回指定类型的任务 |

### Service — update_task_status（3 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 21 | 更新状态 | status 正确变更 |
| 22 | 更新状态同时设置 result | status 和 result 同时更新 |
| 23 | 更新不存在的任务无异常 | 静默忽略 |

### Service — update_task_progress（3 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 24 | 更新进度 | progress 正确设置 |
| 25 | 进度上限 100 | 传入 150 被截断为 100 |
| 26 | 进度下限 0 | 传入 -10 被截断为 0 |

### Service — append_task_log（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 27 | 追加日志 | logs 包含消息内容 |
| 28 | 多条日志按序保留 | first 在 second 之前 |

### TaskRegistry（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 29 | 注册并获取 | register 后 get 返回同一函数 |
| 30 | 获取未注册类型返回 None | get("nonexistent") = None |
| 31 | 列出所有类型 | list_types 返回排序列表 |
| 32 | has 检查 | has("exists") = True, has("nope") = False |
| 33 | 重复注册抛出 ValueError | 同一 task_type 注册两次报错 |

### Pool（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 34 | 解析标准 redis URL | host、port、database 正确 |
| 35 | 解析带密码的 URL | password 正确提取 |
| 36 | 解析最小 URL 使用默认值 | host=localhost, port=6379, db=0 |
| 37 | 未 configure 时 get_redis_settings 抛出 RuntimeError | 错误消息匹配 "not configured" |
| 38 | configure 存储设置 | get_redis_settings 返回正确的 host/port/db |

### WorkerFactory（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 39 | 生成 WorkerSettings 类 | 包含 functions、max_jobs、job_timeout、redis_settings 属性 |
| 40 | 使用自定义 task_* 配置 | TASK_MAX_JOBS=10 → max_jobs=10 |

### Config 集成（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 41 | task_* 字段有默认值 | task_max_jobs=5, task_job_timeout=3600, task_failure_ttl=86400 |
| 42 | task_* 字段可从环境变量覆盖 | 设置 TASK_MAX_JOBS=8 后读取到 8 |

---

## 回测检查清单

```bash
# 1. 全量测试
cd backend && python -m pytest tests/ -v

# 2. 期望结果
# 90 passed

# 3. 单模块测试（调试用）
python -m pytest tests/test_config.py -v
python -m pytest tests/test_database.py -v
python -m pytest tests/test_security.py -v
python -m pytest tests/test_exceptions.py -v
python -m pytest tests/test_response.py -v
python -m pytest tests/test_pagination.py -v
python -m pytest tests/test_cache.py -v
python -m pytest tests/test_dependencies.py -v
python -m pytest tests/test_tasks.py -v
```
