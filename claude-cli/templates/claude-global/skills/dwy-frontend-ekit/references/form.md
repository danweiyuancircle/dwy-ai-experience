# 表单与脱敏（validators / masking）

> 何时读这份：当用户使用本模块的 API 或问法涉及本模块功能时读取（表单校验、zod schema、vee-validate 集成、PII 数据脱敏）。

## validators — 表单校验

```ts
import {
  isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength,
  // 也可用 zod schema 配合 vee-validate
  phoneSchema, emailSchema, idCardSchema, urlSchema,
  requiredSchema, minLengthSchema, maxLengthSchema,
} from '@dwydev/ekit'
```

### 布尔校验函数

| 函数 | 签名 | 规则 |
|------|------|------|
| `isPhone(value)` | `string => boolean` | 中国手机号 1[3-9] 开头 11 位 |
| `isEmail(value)` | `string => boolean` | 基础邮箱 |
| `isIdCard(value)` | `string => boolean` | 18 位身份证（末位允许 X/x） |
| `isUrl(value)` | `string => boolean` | 合法 URL |
| `isRequired(value)` | `any => boolean` | 非空（0 / false 视为有效） |
| `minLength(value, n)` | `(string, number) => boolean` | 最小长度 |
| `maxLength(value, n)` | `(string, number) => boolean` | 最大长度 |

### Zod schema（配合 vee-validate）

```ts
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { phoneSchema, emailSchema } from '@dwydev/ekit'

const schema = toTypedSchema(z.object({
  phone: phoneSchema,
  email: emailSchema,
}))
const { defineField, errors } = useForm({ validationSchema: schema })
```

> `minLengthSchema(n)` / `maxLengthSchema(n)` 是工厂函数，调用后返回 schema。

---

## masking — PII 脱敏

```ts
import {
  maskPhone, maskEmail, maskIdCard, maskBankCard,
  maskName, maskAddress, maskIp, maskLicensePlate, maskText,
} from '@dwydev/ekit'
```

纯函数，无外部依赖。**输入不符合格式时原样返回，不抛异常**。

| 函数 | 规则 | 示例 |
|------|------|------|
| `maskPhone(phone)` | 前 3 后 4 | `'138****5678'` |
| `maskEmail(email)` | 首字符 + `***` + @域名 | `'z***@gmail.com'` |
| `maskIdCard(id)` | 前 3 后 4（18 位） | `'420***********1234'` |
| `maskBankCard(card)` | 前 4 后 4（13~19 位） | `'6222********1234'` |
| `maskName(name)` | 2 字 → 姓+`*`；3+ 字 → 姓+`*`×(n-2)+末字 | `'张*'` / `'张*明'` |
| `maskAddress(addr)` | 保留省/市/区/县/镇/旗前缀 + `****` | `'浙江省杭州市西湖区****'` |
| `maskIp(ip)` | IPv4 末段替换 `*` | `'192.168.1.*'` |
| `maskLicensePlate(plate)` | 前 2 后 1，中间 `***` | `'浙A***8'` |
| `maskText(text, start=1, end=1, ch='*')` | 通用：保留首尾 N 位 | `maskText('1234567890', 2, 3)` → `'12*****890'` |
