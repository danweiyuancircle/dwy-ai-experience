# SDK 接口注释敏感模式清单

`check_comments.py` 的规则源。SDK 对外注释（Python docstring、JSDoc、TSDoc）**只写**功能含义、入参格式、返回值、异常，下列模式一律视为泄露。

## 模式表

| 模式 ID | 正则 | 风险 | 误报豁免（如有） |
|---|---|---|---|
| `internal-domain` | `[\w-]+\.(internal\|corp\|local\|intranet)\b` | 暴露内网域名结构 | 出现在 example.com / your-domain 等示例语 → 视为示例 |
| `private-ip` | `\b(10\.\d+\.\d+\.\d+\|192\.168\.\d+\.\d+\|172\.(1[6-9]\|2\d\|3[01])\.\d+\.\d+)\b` | 暴露内网 IP | — |
| `sql-statement` | `\b(SELECT\|UPDATE\|DELETE\|INSERT)\b[^.]*\b(FROM\|WHERE\|SET\|INTO)\b` | 暴露表结构、查询逻辑 | 行含 `example`/`e.g.` 视作示例语 |
| `redis-key-pattern` | `\b(cache\|redis\|fmt\|lock\|queue):[a-z_]+:` | 暴露缓存键 schema | — |
| `jira-ticket` | `\b[A-Z]{2,6}-\d{2,6}\b` | 暴露内部工单系统 | 行含「示例」「example」豁免 |
| `internal-service` | `\b[a-z_]+_(service\|server\|grpc\|rpc)_(v\d\|prod\|stg\|dev)\b` | 暴露内部服务命名 | — |
| `service-port` | `:(\d{4,5})\b` 且行内含 `connect\|server\|host\|endpoint\|address` | 暴露内网服务端口 | 默认端口 80/443/8080 豁免，example 示例豁免 |
| `internal-email` | `[\w.+-]+@(?!example\.com\|gmail\.com\|outlook\.com)[\w.-]+\.[a-z]{2,}` | 暴露员工邮箱 | 公开公司域名（github.io 等）豁免 |
| `aws-arn` | `arn:aws:[a-z0-9-]+:[a-z0-9-]*:\d+:[a-zA-Z0-9-_/:]+` | 暴露 AWS 账号 ID 与资源 | — |
| `cred-keyword` | `\b(API_KEY\|TOKEN\|SECRET\|PASSWORD\|PRIVATE_KEY)\s*[=:]\s*['"][\w-]+['"]` | 注释里硬编码凭证 | 占位 `xxx` / `<your-token>` 豁免 |
| `aws-key` | `\bAKIA[0-9A-Z]{16}\b` | AWS Access Key ID | — |

## 正例 vs 反例

### Python docstring

**反例**：

```python
def get_user(user_id: str):
    """
    Connect to https://users.internal.corp.com/v2/profile via gRPC.
    Query SELECT * FROM users_prod WHERE id = ? with cache key cache:user:{id}.
    Owner: john.doe@anthropic.io. See PAY-1234 for context.
    """
```

**正例**：

```python
def get_user(user_id: str):
    """
    获取用户基本资料。

    Args:
        user_id: 用户唯一标识符（UUID 格式）。

    Returns:
        UserProfile，含 name / email / created_at 字段。

    Raises:
        UserNotFoundError: user_id 不存在时抛出。
        AuthenticationError: 当前会话无权限读取该用户资料。

    Example:
        >>> user = get_user("user-123")
        >>> user.name
        'Alice'
    """
```

### TypeScript JSDoc

**反例**：

```typescript
/**
 * Fetch user from db.internal.corp:5432 (table users_prod).
 * Uses Redis cache key fmt:user:{id} ttl 3600s.
 * Fallback to backup_db at 10.0.0.5:5432 if primary down.
 * See JIRA USR-456, contact #user-platform on internal Slack.
 */
export async function fetchUser(id: string): Promise<UserProfile> { ... }
```

**正例**：

```typescript
/**
 * 获取用户基本资料。
 *
 * @param id 用户唯一标识符（UUID 格式）
 * @returns 用户资料对象，含 name / email / created_at 字段
 * @throws {UserNotFoundError} id 不存在时抛出
 * @throws {AuthenticationError} 当前会话无权限读取该用户资料
 *
 * @example
 * ```ts
 * const user = await fetchUser("user-123");
 * console.log(user.name);
 * ```
 */
export async function fetchUser(id: string): Promise<UserProfile> { ... }
```

## 应该写什么 vs 不应该写什么

| 类别 | 应该写 | 不应该写 |
|---|---|---|
| 接口功能 | 业务语义（「获取用户资料」） | 实现路径（「调用 gRPC service xxx」） |
| 入参 | 类型、格式、约束（UUID、长度上限） | 上游表字段、内部 schema 字段名 |
| 返回 | 字段语义 | 来自哪张表、哪个缓存键 |
| 异常 | 业务异常类、触发条件 | 数据库连接错误细节、内部 RPC 失败码 |
| 示例 | 公开占位（`user-123` / `example.com`） | 真实用户 ID、真实邮箱、内网域名 |
| 链接 | 公开文档 URL、相对路径文档 | 内网 wiki、JIRA、Slack、Confluence 链接 |

## 行内豁免约定

误报场景在该行追加注释：

- Python：`# sdk-spec: ignore`
- TS/JS：`// sdk-spec: ignore`

豁免**单行**，不豁免整段。要长期豁免某文件 → 在 `<project_root>/.dwy/sdk-spec/config.json` 加 `ignore_files: ["path/to/file.py"]`（未来支持，当前手动用行内豁免）。
