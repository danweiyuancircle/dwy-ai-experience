<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const rate1 = ref(3)
const rate2 = ref(3.5)
const rate3 = ref(4)
const rateDisabled = ref(3.5)

const labels = ['很差', '较差', '一般', '不错', '很好']
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Rate 评分</h1>
    <p class="text-muted-foreground mb-6">星级评分组件，支持半星、最大分值设置、禁用状态。</p>

    <DemoBlock
      title="基础评分"
      description="点击或悬停设置评分"
      code='<ERate v-model="rate" />'
    >
      <div class="space-y-3">
        <ERate v-model="rate1" />
        <p class="text-sm text-muted-foreground">当前评分：{{ rate1 }} 分</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="半星评分"
      description="设置 allowHalf 允许选择半星"
      code='<ERate v-model="rate" :allowHalf="true" />'
    >
      <div class="space-y-3">
        <ERate v-model="rate2" :allowHalf="true" />
        <p class="text-sm text-muted-foreground">当前评分：{{ rate2 }} 分（支持半星）</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="自定义最大分值"
      description="通过 max 设置最大星数"
      code='<ERate v-model="rate" :max="10" />'
    >
      <div class="space-y-3">
        <ERate v-model="rate3" :max="10" />
        <p class="text-sm text-muted-foreground">当前评分：{{ rate3 }} / 10</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="显示文字说明"
      description="设置 showText 在评分右侧显示说明文字"
      code='<ERate v-model="rate" :showText="true" />'
    >
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <ERate v-model="rate1" :showText="true" />
          <span class="text-sm text-muted-foreground">{{ labels[rate1 - 1] || '' }}</span>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="设置 disabled 禁用评分交互（展示模式）"
      code='<ERate v-model="rate" :disabled="true" />'
    >
      <div class="space-y-3">
        <ERate v-model="rateDisabled" :disabled="true" :allowHalf="true" />
        <p class="text-sm text-muted-foreground">展示模式，不可更改（{{ rateDisabled }} 分）</p>
      </div>
    </DemoBlock>
  </div>
</template>
