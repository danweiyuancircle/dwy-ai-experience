<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const basic = ref(false)
const withLabel = ref(true)
const disabled = ref(false)
const sizeSm = ref(true)
const sizeLg = ref(false)
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Switch 开关</h1>
    <p class="text-muted-foreground mb-6">开/关切换组件，支持标签文本、禁用和尺寸变体。</p>

    <DemoBlock
      title="基础开关"
      description="最简单的开关控件"
      code='<ESwitch v-model="value" />'
    >
      <div class="flex items-center gap-4">
        <ESwitch v-model="basic" />
        <span class="text-sm text-muted-foreground">当前：{{ basic ? '开' : '关' }}</span>
      </div>
    </DemoBlock>

    <DemoBlock
      title="带标签"
      description="设置 label 属性显示说明文字"
      code='<ESwitch v-model="value" label="接收通知" />'
    >
      <div class="space-y-3">
        <ESwitch v-model="withLabel" label="接收通知" />
        <ESwitch v-model="basic" label="暗色模式" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="disabled 禁用开关交互"
      code='<ESwitch :disabled="true" label="禁用（关闭）" />
<ESwitch :modelValue="true" :disabled="true" label="禁用（开启）" />'
    >
      <div class="space-y-3">
        <ESwitch v-model="disabled" :disabled="true" label="禁用（关闭）" />
        <ESwitch :modelValue="true" :disabled="true" label="禁用（开启）" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="尺寸变体"
      description="支持 sm / default / lg 三种尺寸"
      code='<ESwitch v-model="value" size="sm" label="小号 sm" />
<ESwitch v-model="value" label="默认尺寸" />
<ESwitch v-model="value" size="lg" label="大号 lg" />'
    >
      <div class="space-y-3">
        <ESwitch v-model="sizeSm" size="sm" label="小号 sm" />
        <ESwitch v-model="basic" label="默认尺寸 default" />
        <ESwitch v-model="sizeLg" size="lg" label="大号 lg" />
      </div>
    </DemoBlock>
  </div>
</template>
