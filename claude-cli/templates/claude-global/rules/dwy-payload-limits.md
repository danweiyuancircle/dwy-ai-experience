# 数据载荷三层长度限制规则

防止大文本 DoS、内存耗尽、带宽滥用。所有涉及用户输入 / HTTP 请求体 / 文件上传的场景必须遵循三层限制,单层失守即高风险。

本文件是"长度 / 大小 / 数量"规则的**唯一权威源**。其他规则文件(`dwy-server-security.md`、`dwy-python-security.md`)的对应章节只做引用,不重复定义。

## 为什么需要三层

- **前端 = UX 边界**:给用户即时反馈,避免无效输入浪费带宽和后端算力
- **网关 = 流量边界**:Nginx / CDN / 负载均衡层拦截异常大请求,保护后端不被打满
- **后端 = 业务边界**:字段级严格校验,阻断绕过前端的恶意请求
- 三层职责不可互相替代。只靠前端易被绕过;只靠后端流量先耗在 TCP/TLS 握手和解析上;只靠网关无法挡住"多个小字段组合起来刚好达到 body 上限"的攻击

三层数字必须对齐:**前端 maxlength ≤ 后端 max_length**,**后端字段累加加冗余 ≤ 网关 client_max_body_size**。

## 第一层:前端输入限制

### 强制规则

- 所有 `<input type="text">` / `<input type="search">` / `<textarea>` 必须设 `maxlength` 属性
- `@dwydev/eui` 的 `EInput` / `ETextarea` / 可搜索 `ESelect` / 可输入 `ETag` 必须传 `maxlength` prop
- 富文本编辑器(tiptap / quill 等)必须配置字符数上限,超出禁止输入
- 文件选择控件必须在前端预校验大小和 MIME 类型(`accept` 属性 + JS 二次校验)
- 批量操作前端必须做分页 / 分批,不允许一次性超过 items 上限
- 表单校验层必须用 zod `.max()` 再补一道,防粘贴 / 脚本绕过 HTML `maxlength`

### 禁止事项

- 禁止 `EInput` / `ETextarea` 不带 `maxlength` 上线
- 禁止富文本编辑器无字符上限
- 禁止"前端不限制,全部让后端兜底"
- 禁止大文件(>10MB)走普通 API 中转

### 示例

```vue
<!-- ✅ 正确 -->
<EInput v-model="form.title" :maxlength="100" show-word-limit />
<ETextarea v-model="form.desc" :maxlength="500" show-word-limit />

<!-- ❌ 违规 -->
<EInput v-model="form.title" />
<ETextarea v-model="form.desc" />
```

配套 zod schema(vee-validate):

```ts
import { z } from 'zod'

const schema = z.object({
  title: z.string().max(100),
  desc: z.string().max(500),
})
```

## 第二层:网关 / 部署限制

### 强制规则

- Nginx `client_max_body_size` 必须显式配置,不允许使用默认值
- 无文件上传业务时:全局 `client_max_body_size 1m`,**禁止** > `10m`
- 有上传业务时:针对上传路径单独放宽(如 `location /api/upload` 设 `20m`),**禁止**全局放宽
- 上传大文件(>10MB)必须走对象存储直传(MinIO / S3 预签名 URL),**禁止**走 API 中转
- CDN / 负载均衡层的 body 限制和超时必须与 Nginx 数字对齐

### 示例

```nginx
# server 块 — 全局默认
client_max_body_size 1m;
client_body_timeout 10s;
client_header_timeout 10s;

# 仅上传路径放宽
location /api/upload {
    client_max_body_size 20m;
    proxy_pass http://127.0.0.1:8000;
}
```

### 违规检测

- Nginx 配置缺少 `client_max_body_size` 或值 > `10m` 但业务不是文件上传
- 大文件上传路由走 API 中转而非对象存储直传
- CDN 和 Nginx 的 body 上限不一致

## 第三层:后端数据校验

### 强制规则

- Pydantic 每个 `str` 字段必须 `max_length`
- Pydantic 每个 `list` 字段必须 `max_length`(限制数组元素数量)
- `Query()` / `Path()` / `Header()` 参数同样必须 `max_length`
- FastAPI 路由必须显式声明 Pydantic schema,**禁止** `data: dict` / `data: Any`
- 分页 `page_size` 必须有 `le`(默认 `le=100`)
- 后端不信任网关,必须在中间件做 request body 大小二次兜底(超出直接 413)
- 图片上传除文件大小外,**必须**校验实际像素尺寸(Pillow `image.size`),防 decompression bomb
- 文件大小后端二次校验,不信任前端声明的 `Content-Length`

### 示例

```python
from pydantic import BaseModel, Field

# ✅ 正确
class UserCreate(BaseModel):
    name: str = Field(max_length=32)
    title: str = Field(max_length=100)
    desc: str = Field(max_length=500)
    tags: list[str] = Field(max_length=20)

class ListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

# ❌ 违规
@router.post("/users")
async def create_user(data: dict): ...

class BadParams(BaseModel):
    page_size: int = 20            # 无 le,攻击者可传 999999
    name: str                       # 无 max_length
    tags: list[str]                 # 无 max_length
```

> 说明:格式校验(`EmailStr` / 手机号 `pattern` / `HttpUrl` / 数字 `ge` / `le` 的数值范围)不是长度议题,仍归属 `dwy-python-security.md` §四,本文件不重复。

## 统一尺寸参考表

三层数字必须对齐。下表为全局默认,项目 CLAUDE.md 可为特殊业务覆盖个别字段(须显式说明原因)。

| 场景 | 前端 maxlength | 后端 max_length | 网关 / 上传 |
|------|---------------|----------------|-------------|
| 用户名 | 32 | 32 | — |
| 邮箱 | 254 | 254(RFC 5321) | — |
| 密码(输入框) | 128 | 128 | — |
| 手机号 | 20 | 20 | — |
| 标题 / 短名称 | 100 | 100 | — |
| 描述 / 摘要 | 500 | 500 | — |
| 正文 / 评论 | 2000 | 2000 | — |
| 富文本(HTML 串) | 100 KB | 100 KB | 走 body_size |
| 搜索关键词 | 100 | 100 | — |
| URL 字段 | 2048 | 2048 | — |
| JSON body(默认) | — | 中间件兜底 1 MB | `client_max_body_size 1m` |
| 图片上传(直发 API) | 前端预检 5 MB | 5 MB + 像素 `<= 8000×8000` | 上传路径 `10m` |
| 通用小文件上传 | 前端预检 10 MB | 10 MB | 上传路径 `20m` |
| 大文件(>10 MB) | — | — | 走对象存储直传,不过 API |
| 批量接口 items | UI 分批 | `max_length=100` | — |
| 查询分页 page_size | — | `le=100` | — |

### 边界原则

- 前端 `maxlength` ≤ 后端 `max_length`(前端更严,UX 明确)
- 后端所有字段 `max_length` 总和加冗余 ≤ 网关 `client_max_body_size`
- 超出表中范围的业务必须在项目 CLAUDE.md 中显式记录并说明原因

## 全局禁止事项

- 禁止任一层以"无限制"上线
- 禁止三层数字互相冲突(例如前端 1000 但后端 100)
- 禁止只靠前端 `maxlength` 而后端不校验
- 禁止只靠后端 `max_length` 而前端不限
- 禁止只靠网关 `client_max_body_size` 而无字段级 `max_length`

## 违规检测

发现以下任一情况,立即停止并提示用户:

1. `.vue` 文件中 `EInput` / `ETextarea` 没有 `maxlength`
2. 富文本组件(tiptap / quill)未配置字符上限
3. Pydantic `BaseModel` 有 `str` 字段但未设 `max_length`
4. Pydantic `BaseModel` 有 `list` 字段但未设 `max_length`
5. FastAPI 路由以 `dict` / `Any` 作为 body 参数
6. 分页参数无 `le` 上限
7. Nginx 配置缺失 `client_max_body_size`,或值 > `10m` 但业务不是文件上传
8. 上传 > 10MB 文件走 API 中转而非对象存储直传
9. 图片上传仅校验文件大小而不校验像素尺寸
