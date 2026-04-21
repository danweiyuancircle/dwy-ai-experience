# @dwydev/ekit 测试用例清单

> 回测基准：188 个测试用例，11 个测试文件。版本变更后必须全部通过。
>
> 运行命令：`cd frontend/ekit && pnpm vitest run`

---

## 1. date 模块（19 个）

`src/date/date.test.ts`

### formatDate
| # | 用例 | 输入 | 预期输出 |
|---|------|------|---------|
| 1 | Date 对象格式化 | `new Date(2025, 0, 5)` | `'2025-01-05'` |
| 2 | 时间戳格式化 | `new Date(2025, 5, 15).getTime()` | `'2025-06-15'` |
| 3 | ISO 字符串格式化 | `'2025-03-01T12:00:00Z'` | 匹配 `YYYY-MM-DD` |
| 4 | 单位数月/日补零 | `new Date(2025, 0, 1)` | `'2025-01-01'` |

### formatDateTime
| # | 用例 | 输入 | 预期输出 |
|---|------|------|---------|
| 5 | 完整日期时间 | `new Date(2025, 5, 15, 9, 5, 3)` | `'2025-06-15 09:05:03'` |
| 6 | 时分秒补零 | `new Date(2025, 0, 1, 0, 0, 0)` | `'2025-01-01 00:00:00'` |

### formatTime
| # | 用例 | 输入 | 预期输出 |
|---|------|------|---------|
| 7 | 时分格式化 | `14:30` | `'14:30'` |
| 8 | 单位数补零 | `8:05` | `'08:05'` |

### formatRelativeTime
| # | 用例 | 场景 | 预期输出 |
|---|------|------|---------|
| 9 | falsy 输入 | `''` / `0` | `''` |
| 10 | < 1 分钟 | 30 秒前 | `'刚刚'` |
| 11 | < 60 分钟 | 10 分钟前 | `'10 分钟前'` |
| 12 | < 24 小时 | 3 小时前 | `'3 小时前'` |
| 13 | < 30 天 | 7 天前 | `'7 天前'` |
| 14 | >= 30 天 | 90 天前 | `'2025-01-01'`（YYYY-MM-DD） |
| 15 | 时间戳输入 | number | 正确解析 |
| 16 | ISO 字符串输入 | string | 正确解析 |

### formatBy
| # | 用例 | 输入 | 预期输出 |
|---|------|------|---------|
| 17 | 自定义模板 | `'YYYY/MM/DD'` | `'2025/06/15'` |
| 18 | 时间戳 + 模板 | number + `'MM-DD'` | 正确格式 |
| 19 | ISO 字符串 + 模板 | string + `'YYYY'` | 年份字符串 |

---

## 2. request 模块（15 个）

`src/request/request.test.ts`

### createRequest
| # | 用例 |
|---|------|
| 1 | 使用默认选项创建 axios 实例 |
| 2 | 使用自定义选项创建 |
| 3 | 注册请求和响应拦截器 |

### tokenPlugin
| # | 用例 |
|---|------|
| 4 | token 存在时设置 Authorization header |
| 5 | token 为 null 时不设置 header |

### headerPlugin
| # | 用例 |
|---|------|
| 6 | 值存在时设置自定义 header |
| 7 | 值为 null 时不设置 header |

### unwrapPlugin
| # | 用例 |
|---|------|
| 8 | code=200 时返回解包数据 |
| 9 | code≠200 时 reject |
| 10 | message 为空时使用默认消息 |
| 11 | 非包装响应透传 |

### refreshTokenPlugin
| # | 用例 |
|---|------|
| 12 | 401 时调用 refreshFn 并重试请求 |
| 13 | 无 refresh token 时调用 onRefreshFail |
| 14 | 登录 URL 跳过刷新 |
| 15 | 从响应数据提取错误消息 |

---

## 3. validators 模块（40 个）

`src/validators/validators.test.ts`

### 布尔函数（21 个）

| 函数 | 用例数 | 测试要点 |
|------|--------|---------|
| isPhone | 4 | 合法号码、非 1[3-9] 开头、长度错误、非数字 |
| isEmail | 2 | 合法邮箱、无效格式（无@、空、含空格） |
| isIdCard | 3 | 18 位数字、末位 X/x、长度错误、非数字 |
| isUrl | 2 | http/https/ftp、无效 URL |
| isRequired | 6 | null/undefined、空字符串/空格、空数组、非空字符串、非空数组、数字/布尔 |
| minLength | 2 | 满足最小长度、不足 |
| maxLength | 2 | 满足最大长度、超出 |

### Zod Schema（19 个）

| Schema | 用例数 | 测试要点 |
|--------|--------|---------|
| phoneSchema | 2 | safeParse 成功 + 失败消息 |
| emailSchema | 2 | safeParse 成功 + 失败消息 |
| idCardSchema | 2 | safeParse 成功 + 失败消息 |
| urlSchema | 3 | http 成功、ftp 成功、失败消息 |
| requiredSchema | 4 | 非空成功、空值失败、纯空格失败、空数组失败 |
| minLengthSchema | 3 | 成功、失败、不同 min 值 |
| maxLengthSchema | 3 | 成功、失败、不同 max 值 |

---

## 4. storage 模块（12 个）

`src/storage/storage.test.ts`

| # | 分组 | 用例 |
|---|------|------|
| 1-6 | set + get | 字符串、对象、数组、数字、布尔、null |
| 7-9 | get 默认值 | key 不存在、无默认返回 undefined、有值时忽略默认 |
| 10 | 非 JSON | JSON 解析失败时返回原始值 |
| 11 | remove | 删除 key |
| 12 | clear | 清空所有 |

---

## 5. cookie 模块（13 个）

`src/cookie/cookie.test.ts`

| # | 分组 | 用例 |
|---|------|------|
| 1-5 | set + get | 字符串、对象（JSON）、数组、数字、布尔 |
| 6 | get | 不存在的 key 返回 undefined |
| 7 | remove | 删除 cookie |
| 8 | useCookie | 创建 ref 读取当前值 |
| 9 | useCookie | 不存在时使用默认值 |
| 10 | useCookie | 修改 ref 同步到 cookie |
| 11 | useCookie | 设为 undefined 删除 cookie |
| 12 | useCookie | 设为 null 删除 cookie |
| 13 | useCookie | 对象变更同步 |

---

## 6. copy 模块（6 个）

`src/copy/copy.test.ts`

| # | 用例 |
|---|------|
| 1 | copyText 调用 clipboard.writeText |
| 2 | useClipboard.isSupported 为 true |
| 3 | copy 后 text 和 copied 更新 |
| 4 | 1500ms 后 copied 重置为 false |
| 5 | 无 clipboard 时 isSupported 为 false |
| 6 | 无 clipboard 时 copy 不执行 |

---

## 7. qs 模块（9 个）

`src/qs/qs.test.ts`

| # | 分组 | 用例 |
|---|------|------|
| 1 | stringify | 基本对象序列化 |
| 2 | stringify | 数组使用 repeat 格式 |
| 3 | stringify | 默认不加 `?` 前缀 |
| 4 | parse | 基本解析 |
| 5 | parse | 自动忽略 `?` 前缀 |
| 6 | 往返 | stringify → parse 还原一致 |
| 7 | options | stringify 覆盖 addQueryPrefix |
| 8 | options | stringify 覆盖 arrayFormat |
| 9 | options | parse 关闭 ignoreQueryPrefix |

---

## 8. file 模块（16 个）

`src/file/file.test.ts`

### formatFileSize（8 个）
| # | 输入 | 预期 |
|---|------|------|
| 1 | 0 | `'0 B'` |
| 2 | 500 | `'500 B'` |
| 3 | 1024 | `'1 KB'` |
| 4 | 1048576 | `'1 MB'` |
| 5 | 1073741824 | `'1 GB'` |
| 6 | 1099511627776 | `'1 TB'` |
| 7 | decimals=0 | 无小数 |
| 8 | 小数值 | 正确精度 |

### saveBlob（1 个）
| # | 用例 |
|---|------|
| 9 | 调用 file-saver 的 saveAs |

### downloadFile（7 个）
| # | 用例 |
|---|------|
| 10 | 默认 GET 请求 + saveAs |
| 11 | POST 方法 + data |
| 12 | 从 Content-Disposition 解析文件名 |
| 13 | UTF-8 编码文件名 |
| 14 | 无文件名时 fallback 为 `'download'` |
| 15 | 显式 filename 优先于 header |
| 16 | 传递自定义 headers |

---

## 9. hooks 模块（4 个）

`src/hooks/hooks.test.ts`

| # | 用例 |
|---|------|
| 1 | useDebounce 返回初始值 |
| 2 | useDebounce 延迟更新值 |
| 3 | useDebounce 快速变化只保留最后值 |
| 4 | useDebounce 默认 300ms 延迟 |

---

## 10. hooks/vueuse 模块（5 个）

`src/hooks/vueuse.test.ts`

| # | 用例 |
|---|------|
| 1 | useWindowSize 返回 width/height ref |
| 2 | useMediaQuery 返回布尔 ref |
| 3 | useThrottle 是函数 |
| 4 | useIntersectionObserver 是函数 |
| 5 | useResizeObserver 是函数 |

---

## 11. masking 模块（49 个）

`src/masking/masking.test.ts`

| 函数 | 用例数 | 测试要点 |
|------|--------|---------|
| maskPhone | 6 | 标准号码、空字符串、长度错误、非数字、不同号段 |
| maskEmail | 6 | 标准邮箱、空字符串、无@、单字符用户名、多字符、多@符号 |
| maskIdCard | 5 | 18位、末位X、空字符串、格式不匹配、15位原样返回 |
| maskBankCard | 5 | 16位、19位、空字符串、位数太短、非数字 |
| maskName | 5 | 2字、3字、4字、空字符串、单字 |
| maskAddress | 7 | 省市区、省市、自治区、直辖市、不匹配长/短地址、空字符串 |
| maskIp | 4 | 标准IPv4、空字符串、非IP、只有3段 |
| maskLicensePlate | 4 | 标准7位、新能源8位、空字符串、格式不匹配 |
| maskText | 7 | 默认参数、自定义start/end、自定义maskChar、空字符串、长度不足、start=0、end=0 |

---

## 回测检查清单

```bash
# 1. 全量测试
cd frontend/ekit && pnpm vitest run

# 2. 期望结果
# Test Files  11 passed (11)
# Tests       188 passed (188)

# 3. 单模块测试（调试用）
pnpm vitest run src/date
pnpm vitest run src/request
pnpm vitest run src/validators
pnpm vitest run src/storage
pnpm vitest run src/cookie
pnpm vitest run src/copy
pnpm vitest run src/qs
pnpm vitest run src/file
pnpm vitest run src/hooks
pnpm vitest run src/masking
```
