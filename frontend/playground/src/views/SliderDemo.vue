<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const single = ref([50])
const range = ref([20, 80])
const stepped = ref([30])
const disabled = ref([60])
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Slider 滑块</h1>
    <p class="text-muted-foreground mb-6">滑动输入组件，支持单滑块、范围选择、步长设置和禁用状态。</p>

    <DemoBlock
      title="基础滑块"
      description="单滑块，拖动选择值"
      code='<ESlider v-model="value" :min="0" :max="100" />'
    >
      <div class="space-y-4">
        <ESlider v-model="single" :min="0" :max="100" />
        <p class="text-sm text-muted-foreground">当前值：{{ single[0] }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="范围选择"
      description="通过双值数组实现范围选择滑块"
      code='<ESlider v-model="range" :min="0" :max="100" />'
    >
      <div class="space-y-4">
        <ESlider v-model="range" :min="0" :max="100" />
        <p class="text-sm text-muted-foreground">范围：{{ range[0] }} — {{ range[1] }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="步长设置"
      description="通过 step 设置每次移动的步长"
      code='<ESlider v-model="value" :min="0" :max="100" :step="10" />'
    >
      <div class="space-y-4">
        <ESlider v-model="stepped" :min="0" :max="100" :step="10" />
        <p class="text-sm text-muted-foreground">当前值：{{ stepped[0] }}（步长 10）</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="设置 disabled 禁用拖动"
      code='<ESlider v-model="value" :disabled="true" />'
    >
      <ESlider v-model="disabled" :disabled="true" />
    </DemoBlock>

    <DemoBlock
      title="音量控制示例"
      description="Slider 在实际场景中的应用"
    >
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-12">音量</span>
          <ESlider v-model="single" :min="0" :max="100" class="flex-1" />
          <span class="text-sm font-medium w-8">{{ single[0] }}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-12">亮度</span>
          <ESlider v-model="stepped" :min="0" :max="100" :step="5" class="flex-1" />
          <span class="text-sm font-medium w-8">{{ stepped[0] }}%</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-12">价格</span>
          <ESlider v-model="range" :min="0" :max="1000" :step="50" class="flex-1" />
          <span class="text-sm font-medium w-24">¥{{ range[0] }}-{{ range[1] }}</span>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
