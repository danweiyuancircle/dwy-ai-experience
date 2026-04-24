# dwyeapi 测试用例清单

> 本文件列出 eapi 核心模块和本轮 environment 机制相关的用例。providers 模块的完整用例清单暂未全量纳入。
>
> 运行命令：`cd backend && python -m pytest tests/ -v`

---

## 1. config 模块（14 个）

`tests/test_config.py`

### BaseSettings

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 缺少必填环境变量时抛出 ValueError | 未设置 DATABASE_URL / REDIS_URL / SECRET_KEY 时构造失败 |
| 2 | 设置所有必填字段后正确构造 | database_url、redis_url、secret_key 均正确赋值 |
| 3 | debug 字段已废弃 | BaseSettings() 实例无 `debug` 属性,调试开关统一走 environment |
| 4 | allowed_origins 默认为空列表 | 未设置 ALLOWED_ORIGINS 时为 `[]` |
| 5 | 从环境变量解析 allowed_origins | JSON 数组字符串正确解析为 `list[str]` |
| 6 | 子类可扩展自定义字段 | 继承 BaseSettings 后新增字段可从环境变量读取 |
| 7 | JWT 相关字段有合理默认值 | jwt_algorithm 默认 `"HS256"`，access_token_expire_minutes 默认 `30` |

### Environment（dev / prod）

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | environment 默认 prod | 未设置 ENVIRONMENT 时 `is_prod()` 为 True |
| 9 | ENVIRONMENT=dev 可切换 | 环境变量 dev 时 `is_dev()` 为 True |
| 10 | 非法值抛 ValidationError | ENVIRONMENT=staging 构造失败 |
| 11 | get_environment() 返回当前值 | 实例化 dev 后读到 "dev" |
| 12 | is_dev / is_prod 互斥 | set_current_environment 切换后状态互斥 |
| 13 | 业务子类继承后自动同步 | MySettings(BaseSettings)() 也会触发全局同步 |
| 14 | 模块初始值为 prod | 未实例化前的 fail-safe 默认值 |

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

## 4. exceptions 模块（15 个）

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

### ExceptionHandlers — AppError 子类（4 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 7 | NotFoundError → 404 | 响应体符合 ApiResponse 信封（code/message/data=null/timestamp） |
| 8 | BusinessError → 422 | 响应体符合 ApiResponse 信封，code 为业务错误码 |
| 9 | PermissionDeniedError → 403 | HTTP 状态码正确映射，code=PERMISSION_DENIED |
| 10 | AuthenticationError → 401 | HTTP 状态码正确映射，code=AUTHENTICATION_FAILED |

### ExceptionHandlers — 框架异常（5 个,0.7.0 新增）

| # | 用例 | 测试要点 |
|---|------|---------|
| 11 | RequestValidationError → 422 + 结构化 errors | code=`VALIDATION_ERROR`,message=`请求参数校验失败`,data.errors 为 `[{field, message}]` 列表 |
| 12 | HTTPException → 透传状态码 + headers | 418 响应码,`code=HTTP_418`,响应头 `X-Test: yes` 透传 |
| 13 | HTTPException OAuth2 `WWW-Authenticate` 保留 | 401 响应头 `WWW-Authenticate: Bearer` 不丢失 |
| 14 | 未捕获 Exception dev 模式含详情 | ENVIRONMENT=dev 时 message 含 `str(exc)`(如 KeyError 字段名),便于调试 |
| 15 | 未捕获 Exception prod 模式脱敏 | ENVIRONMENT=prod 时 message 固定 `服务器内部错误`,内部信息(字段名等)不泄露 |

---

## 5. response 模块（13 个）

`tests/test_response.py`

### ApiResponseOk（5 个）— `ApiResponse.ok(data)`

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 默认 code 和 message | code="SUCCESS"、message="success"、timestamp 为 int |
| 2 | 自定义 message | 传入 message="created" 正确覆盖，code 仍为 SUCCESS |
| 3 | data 可为 None | 不传 data 时 data=None |
| 4 | data 为 Pydantic 模型 | model_dump 正确序列化嵌套数据 |
| 5 | 序列化结构 | 字段集合为 {code, message, data, timestamp} |

### ApiResponsePage（4 个）— `ApiResponse.page(items, total, page, page_size)`

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | 分页结构 | data 为 PageData 实例，items/total/page/page_size 正确赋值 |
| 7 | 分页序列化 | model_dump 输出 {items, total, page, page_size} 四字段 |
| 8 | 空分页 | items=[]、total=0 合法 |
| 9 | 自定义 message | 分页响应可携带自定义提示信息 |

### ApiResponseDirectConstruction（2 个）— 错误态直接实例化

| # | 用例 | 测试要点 |
|---|------|---------|
| 10 | 自定义 code 构造 | code="NOT_FOUND"、data=None，供 handler 使用 |
| 11 | 错误响应序列化 | 输出 {code, message, data: null, timestamp} |

### PageData（2 个）— 独立使用

| # | 用例 | 测试要点 |
|---|------|---------|
| 12 | 独立实例化 | PageData[Item] 泛型实例化正确 |
| 13 | from_attributes | `model_validate` 可从对象属性构造 |

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

## 10. masking 模块（61 个）

`tests/test_masking.py`

### mask_phone（7 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 标准手机号 | `13812345678` → `138****5678` |
| 2 | 另一个手机号 | `15099998888` → `150****8888` |
| 3 | 空字符串 | 原样返回 |
| 4 | 长度不足 | 原样返回 |
| 5 | 长度过长 | 原样返回 |
| 6 | 非数字 | 原样返回 |
| 7 | 带国际区号 | 原样返回 |

### mask_email（6 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 8 | 标准邮箱 | `zhangsan@gmail.com` → `z***@gmail.com` |
| 9 | 单字符用户名 | `a@example.com` → `a***@example.com` |
| 10 | 空字符串 | 原样返回 |
| 11 | 无 @ 符号 | 原样返回 |
| 12 | 多个 @ 符号 | 原样返回 |
| 13 | 短用户名 | 首字符 + `***@` + 域名 |

### mask_id_card（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 14 | 标准 18 位 | `420123199001011234` → `420***********1234` |
| 15 | 末位 X | `42012319900101123X` → `420***********123X` |
| 16 | 空字符串 | 原样返回 |
| 17 | 长度不对 | 原样返回 |
| 18 | 非身份证格式 | 原样返回 |

### mask_bank_card（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 19 | 16 位卡号 | 前 4 + `*` 补齐 + 后 4 |
| 20 | 19 位卡号 | 前 4 + `*` 补齐 + 后 4 |
| 21 | 空字符串 | 原样返回 |
| 22 | 长度不足 | 原样返回 |
| 23 | 非数字 | 原样返回 |

### mask_name（7 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 24 | 两字姓名 | `张三` → `张*` |
| 25 | 三字姓名 | `张三明` → `张*明` |
| 26 | 四字姓名 | `欧阳三明` → `欧**明` |
| 27 | 单字 | 原样返回 |
| 28 | 空字符串 | 原样返回 |
| 29 | 英文两字 | `AB` → `A*` |
| 30 | 英文长名 | `Alice` → `A***e` |

### mask_address（9 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 31 | 完整省市区 | 匹配到区后 + `****` |
| 32 | 省市区（深圳） | 匹配到区后 + `****` |
| 33 | 直辖市 | `北京市朝阳区` + `****` |
| 34 | 自治区 | 匹配到区后 + `****` |
| 35 | 含镇 | 匹配到镇后 + `****` |
| 36 | 不匹配长地址 | 保留前 6 字符 + `****` |
| 37 | 不匹配短地址 | 原样返回 |
| 38 | 空字符串 | 原样返回 |
| 39 | 含县 | 匹配到县后 + `****` |

### mask_ip（6 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 40 | 标准 IPv4 | `192.168.1.100` → `192.168.1.*` |
| 41 | 简单 IP | `10.0.0.1` → `10.0.0.*` |
| 42 | 空字符串 | 原样返回 |
| 43 | 非 IP | 原样返回 |
| 44 | IPv6 | 原样返回 |
| 45 | 不完整 IP | 原样返回 |

### mask_license_plate（6 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 46 | 标准车牌 | `浙A12345` → `浙A***5` |
| 47 | 新能源车牌 | `浙AD12345` → `浙A***5` |
| 48 | 另一个车牌 | `京B88888` → `京B***8` |
| 49 | 空字符串 | 原样返回 |
| 50 | 太短 | 原样返回 |
| 51 | 非车牌 | 原样返回 |

### mask_text（10 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 52 | 默认参数 | `abcdef` → `a****f` |
| 53 | 自定义 start/end | `1234567890` → `12*****890` |
| 54 | 自定义 mask_char | `#` 替换 |
| 55 | 空字符串 | 原样返回 |
| 56 | 单字符 | 原样返回 |
| 57 | 两字符默认 | 原样返回 |
| 58 | start+end 超过长度 | 原样返回 |
| 59 | start+end 等于长度 | 原样返回 |
| 60 | start 为 0 | 不保留头部 |
| 61 | end 为 0 | 不保留尾部 |

---

## 11. logger 模块（12 个）

`tests/test_logger.py`

### ConfigureConsole（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 仅控制台不生成文件 | `log_dir=None` 时 tmp 目录仍为空 |
| 2 | 控制台写入 stderr | `capsys` 能捕获到日志内容 |

### ConfigureFile（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 3 | 生成按日期命名文件 | `app_YYYY-MM-DD.log` 存在,内容包含写入的消息 |
| 4 | 按大小触发轮转 | `max_bytes=1024` 条件下产生 ≥2 个文件 |

### GetLogger（6 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 5 | 绑定 module 字段 | `get_logger("user_service")` 日志包含 `user_service` |
| 6 | 无名调用返回默认 logger | 返回非 None 对象 |
| 7 | 返回值是 facade 不是 loguru | `type(log)` 为 `dwyeapi.logger.Logger`，模块名不含 `loguru` |
| 8 | facade 支持 `%s` 位置参数格式化 | `info("a=%s b=%s", 1, 2)` 写入 `a=1 b=2`，原文不含 `%s` |
| 9 | facade 无 args 时保留原文 | 消息含 `{}` / `%%` 等字符时不做格式化，原样写入 |
| 10 | facade 支持 `exc_info=True` 记录堆栈 | 在 except 块中 `error("...", exc_info=True)` 写入 traceback |

### InterceptStdlib（1 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 11 | stdlib 日志进入文件 | `logging.getLogger("x").info(...)` 写入 eapi logger 的文件 |

### CloseAndReconfigure（1 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 12 | close 后可重新 configure | 再次配置后日志写入正常 |

---

## 12. health 模块（7 个,0.7.0 新增）

`tests/test_health.py`

### HealthRouter（5 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 1 | 默认 `/health` 路径返回 alive | 200,`code=SUCCESS`,data `{service, version, status:"alive"}` 正确 |
| 2 | 自定义 `path="/api/healthz"` | 新路径 200,旧 `/health` 404 |
| 3 | `include_in_schema=False` 隐藏于 OpenAPI | `GET /openapi.json` 的 `paths` 不含该路径 |
| 4 | 默认 `include_in_schema=True` 暴露于 OpenAPI | OpenAPI `paths` 含 `/health` |
| 5 | 响应信封形状 | 字段集合 `{code, message, data, timestamp}`,data 子字段 `{service, version, status}` |

### 参数化回显（2 个）

| # | 用例 | 测试要点 |
|---|------|---------|
| 6 | `svc-a / 0.0.1` 组合回显 | data.service / data.version 与入参一致 |
| 7 | `svc-b / 10.20.30` 组合回显 | data.service / data.version 与入参一致 |

> 注:`create_health_router` 内部不调用任何数据库 / Redis / 外部服务,"只探活不探依赖"的设计通过代码审查即可验证,未单独写验证依赖缺席的测试。

---

## 13. providers factory 环境校验（5 个,位于 `tests/providers/`）

`tests/providers/test_email_factory.py` 和 `tests/providers/test_sms_factory.py` 中与 environment 机制相关的新增用例:

| # | 文件 | 用例 | 测试要点 |
|---|------|------|---------|
| 1 | test_email_factory.py | test_mock_provider_forbidden_in_prod | prod + mock → ValueError,消息含 `EMAIL__PROVIDER=mock` |
| 2 | test_email_factory.py | test_resend_provider_unaffected_in_prod | prod + resend 正常构造(回归保护) |
| 3 | test_sms_factory.py | test_mock_provider_forbidden_in_prod | prod + mock → ValueError,消息含 `SMS__PROVIDER=mock` |
| 4 | test_sms_factory.py | test_aliyun_provider_unaffected_in_prod | prod + aliyun 正常构造(回归保护) |
| 5 | tests/providers/conftest.py | autouse fixture 默认 dev | 非环境校验类用例在 dev 下跑,不污染既有 mock 测试 |

> 注: providers 模块其余测试用例(email/sms base、各 provider 实现)暂未纳入本文件,与代码保持同步由开发者各自维护。

---

## 回测检查清单

```bash
# 1. 全量测试
cd backend && python -m pytest tests/ -v

# 2. 期望结果
# 212 passed(0.7.0 新增 12 个:exceptions +5,health +7)
# 允许 2 个预先存在的 tests/providers/test_sms_base.py::test_verify_code_* 失败,与本次改动无关

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
python -m pytest tests/test_masking.py -v
python -m pytest tests/test_logger.py -v
python -m pytest tests/test_health.py -v
```
