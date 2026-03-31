<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const basic = ref('')
const clearable = ref('可清除的文字')
const password = ref('')
const disabled = ref('禁用状态的输入框')
const readonly = ref('只读状态的值')
const sizeSmall = ref('')
const sizeLarge = ref('')
const maxLen = ref('')
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Input 输入框</h1>
    <p class="text-muted-foreground mb-6">基础文本输入组件，支持清除、密码模式、尺寸变体等特性。</p>

    <DemoBlock
      title="基础用法"
      description="最简单的输入框"
      code='<EInput v-model="value" placeholder="请输入内容" />'
    >
      <div class="space-y-3 max-w-sm">
        <EInput v-model="basic" placeholder="请输入内容" />
        <p class="text-sm text-muted-foreground">当前值：{{ basic || '(空)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="可清除"
      description="设置 clearable 显示清除按钮"
      code='<EInput v-model="value" clearable placeholder="输入后可清除" />'
    >
      <div class="space-y-3 max-w-sm">
        <EInput v-model="clearable" clearable placeholder="输入后可清除" />
        <p class="text-sm text-muted-foreground">当前值：{{ clearable || '(已清除)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="密码输入"
      description="设置 showPassword 启用密码可见切换"
      code='<EInput v-model="password" type="password" showPassword placeholder="输入密码" />'
    >
      <div class="max-w-sm">
        <EInput v-model="password" type="password" :showPassword="true" placeholder="输入密码" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用与只读"
      description="disabled 完全禁用，readonly 仅限只读"
      code='<EInput :disabled="true" value="禁用状态" />
<EInput :readonly="true" value="只读状态" />'
    >
      <div class="space-y-3 max-w-sm">
        <EInput v-model="disabled" :disabled="true" placeholder="禁用状态" />
        <EInput v-model="readonly" :readonly="true" placeholder="只读状态" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="尺寸变体"
      description="支持 sm / default / lg 三种尺寸"
      code='<EInput size="sm" placeholder="小尺寸" />
<EInput size="default" placeholder="默认尺寸" />
<EInput size="lg" placeholder="大尺寸" />'
    >
      <div class="space-y-3 max-w-sm">
        <EInput v-model="sizeSmall" size="sm" placeholder="小尺寸 sm" />
        <EInput placeholder="默认尺寸 default" />
        <EInput v-model="sizeLarge" size="lg" placeholder="大尺寸 lg" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="最大长度"
      description="通过 maxlength 限制输入字符数"
      code='<EInput v-model="value" :maxlength="20" placeholder="最多输入 20 个字符" />'
    >
      <div class="max-w-sm">
        <EInput v-model="maxLen" :maxlength="20" placeholder="最多输入 20 个字符" />
        <p class="text-sm text-muted-foreground mt-2">{{ maxLen.length }}/20</p>
      </div>
    </DemoBlock>
  </div>
</template>
