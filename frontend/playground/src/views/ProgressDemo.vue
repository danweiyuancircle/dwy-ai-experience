<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const staticVal = ref(65)
const sliderVal = ref([65])
const animatedVal = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function startAnimation() {
  if (timer) return
  animatedVal.value = 0
  timer = setInterval(() => {
    if (animatedVal.value >= 100) {
      clearInterval(timer!)
      timer = null
    } else {
      animatedVal.value = Math.min(100, animatedVal.value + 2)
    }
  }, 50)
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Progress 进度条</h1>
    <p class="text-muted-foreground mb-6">线性进度条组件，用于展示任务完成进度。</p>

    <DemoBlock
      title="不同进度值"
      description="通过 modelValue 设置 0-100 的进度值"
      code='<EProgress :modelValue="25" />
<EProgress :modelValue="50" />
<EProgress :modelValue="75" />
<EProgress :modelValue="100" />'
    >
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-8">25%</span>
          <EProgress :model-value="25" class="flex-1" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-8">50%</span>
          <EProgress :model-value="50" class="flex-1" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-8">75%</span>
          <EProgress :model-value="75" class="flex-1" />
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground w-8">100%</span>
          <EProgress :model-value="100" class="flex-1" />
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="可交互进度"
      description="通过滑块动态调整进度值"
    >
      <div class="space-y-4">
        <EProgress :model-value="sliderVal[0]" />
        <div class="flex items-center gap-3">
          <ESlider v-model="sliderVal" :min="0" :max="100" class="flex-1" />
          <span class="text-sm font-medium w-12 text-right">{{ sliderVal[0] }}%</span>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="动画进度"
      description="模拟上传/处理进度动画效果"
      code='// 通过定时器更新进度值来实现动画
const progress = ref(0)
const timer = setInterval(() => {
  progress.value = Math.min(100, progress.value + 2)
}, 50)'
    >
      <div class="space-y-4">
        <EProgress :model-value="animatedVal" />
        <div class="flex items-center gap-3">
          <EButton @click="startAnimation" :disabled="timer !== null">
            {{ animatedVal === 100 ? '重新开始' : '开始动画' }}
          </EButton>
          <span class="text-sm text-muted-foreground">{{ animatedVal }}%</span>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
