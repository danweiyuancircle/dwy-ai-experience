<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## validators — 校验函数

\`\`\`ts
import { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from '@dwydev/ekit'
\`\`\`

| 函数 | 签名 | 规则 |
|------|------|------|
| isPhone | \`(value: string) => boolean\` | 中国手机号 1[3-9]开头 11 位 |
| isEmail | \`(value: string) => boolean\` | 基础邮箱格式 |
| isIdCard | \`(value: string) => boolean\` | 18 位身份证（末位可为 X/x） |
| isUrl | \`(value: string) => boolean\` | 使用 \`new URL()\` 校验 |
| isRequired | \`(value: any) => boolean\` | 非 null/undefined/空字符串/空数组。0 和 false 视为有效 |
| minLength | \`(value: string, min: number) => boolean\` | 最小长度 |
| maxLength | \`(value: string, max: number) => boolean\` | 最大长度 |
`
</script>

<template>
  <DocPage :content="content" />
</template>
