<script setup lang="ts">
import { ref } from 'vue'
import { EAlert, EButton, ECard, ETransition } from '@dwydev/eui'
import { EMotionList } from '@dwydev/eui/motion'
import type { ETransitionProps } from '@dwydev/eui'

const preset = ref<NonNullable<ETransitionProps['preset']>>('fade')
const visible = ref(true)
const tasks = ref([
  { id: 1, title: '新提交的工单' },
  { id: 2, title: '待审核的内容' },
  { id: 3, title: '即将到期的任务' },
])
let nextId = 4

function reorder() {
  tasks.value = [...tasks.value].reverse()
}

function add() {
  tasks.value = [...tasks.value, { id: nextId, title: '待处理事项 ' + nextId }]
  nextId++
}
</script>

<template>
  <div class="max-w-3xl space-y-5">
    <header>
      <h1 class="text-2xl font-bold">动效</h1>
      <p class="text-muted-foreground mt-2 text-sm">基础转场独立使用，列表增删与重排使用布局动效。两者均遵循系统的减少动态效果设置。</p>
    </header>
    <ECard title="内容转场">
      <div class="mb-3 flex flex-wrap items-center gap-2">
        <label for="motion-preset" class="text-sm">预设</label>
        <select id="motion-preset" v-model="preset" class="border-input bg-background rounded-md border px-2 py-1 text-sm">
          <option value="fade">淡入淡出</option>
          <option value="slide-up">轻移</option>
          <option value="scale">轻缩放</option>
        </select>
        <EButton size="sm" variant="outline" @click="visible = !visible">{{ visible ? '隐藏提示' : '显示提示' }}</EButton>
      </div>
      <ETransition :preset="preset">
        <EAlert v-if="visible" title="筛选条件已更新" />
      </ETransition>
    </ECard>
    <ECard title="列表增删与重排">
      <div class="mb-3 flex flex-wrap gap-2">
        <EButton size="sm" variant="outline" @click="reorder">反转顺序</EButton>
        <EButton size="sm" variant="outline" @click="add">新增事项</EButton>
      </div>
      <EMotionList :items="tasks" item-key="id" class="space-y-2">
        <template #default="{ item }">
          <div class="flex items-center justify-between gap-2 rounded-md border px-3 py-1.5 text-sm">
            {{ item.title }}
            <EButton size="sm" variant="ghost" :aria-label="'移除' + item.title" @click="tasks = tasks.filter(task => task.id !== item.id)">移除</EButton>
          </div>
        </template>
      </EMotionList>
    </ECard>
    <p class="text-muted-foreground text-sm">
      需要动画编排、手势或共享布局时，可直接使用
      <a class="underline" href="https://motion.dev/docs/vue">Motion for Vue</a>。
    </p>
  </div>
</template>
