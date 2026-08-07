<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## masking — PII 脱敏

\`\`\`python
from dwyeapi import masking
# 或 from dwyeapi.masking import mask_phone, mask_email, ...
\`\`\`

纯函数：非法/空输入**原样返回**，不抛异常。

| 函数 | 示例 |
|------|------|
| mask_phone | \`138****5678\` |
| mask_email | \`z***@gmail.com\` |
| mask_id_card | 身份证号掩码 |
| mask_bank_card | 银行卡掩码 |
| mask_name | 姓名掩码 |
| mask_address | 地址掩码 |
| mask_ip | IP 掩码 |
| mask_license_plate | 车牌掩码 |
| mask_text | 通用文本掩码 |

### 示例

\`\`\`python
from dwyeapi.masking import mask_phone, mask_email

assert mask_phone("13812345678") == "138****5678"
assert mask_email("alice@example.com").startswith("a")
\`\`\`

适用于日志、列表接口、导出前的字段脱敏。
`
</script>

<template>
  <DocPage :content="content" />
</template>
