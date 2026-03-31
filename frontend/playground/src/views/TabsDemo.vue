<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const activeTab = ref('overview')
const dynamicTab = ref('tab1')

const basicItems = [
  { key: 'overview', label: '概览' },
  { key: 'details', label: '详情' },
  { key: 'settings', label: '设置' },
]

const dynamicItems = [
  { key: 'tab1', label: '标签一' },
  { key: 'tab2', label: '标签二' },
  { key: 'tab3', label: '标签三（禁用）', disabled: true },
  { key: 'tab4', label: '标签四' },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Tabs 标签页</h1>
    <p class="text-muted-foreground mb-6">标签页组件，支持内容切换和禁用状态。</p>

    <DemoBlock
      title="基础标签页"
      description="使用 items 数组定义标签，v-model 绑定当前激活的 key"
      code='<ETabs v-model="activeTab" :items="items">
  <template #overview>概览内容</template>
  <template #details>详情内容</template>
</ETabs>'
    >
      <ETabs v-model="activeTab" :items="basicItems">
        <template #overview>
          <div class="p-4 bg-muted/30 rounded-md">
            <h4 class="font-medium mb-2">概览</h4>
            <p class="text-sm text-muted-foreground">这里显示概览信息，包括统计数据和关键指标。</p>
          </div>
        </template>
        <template #details>
          <div class="p-4 bg-muted/30 rounded-md">
            <h4 class="font-medium mb-2">详情</h4>
            <p class="text-sm text-muted-foreground">这里显示详细信息，包括完整的数据和配置项。</p>
          </div>
        </template>
        <template #settings>
          <div class="p-4 bg-muted/30 rounded-md">
            <h4 class="font-medium mb-2">设置</h4>
            <div class="space-y-2">
              <ESwitch :modelValue="true" label="接收通知" />
              <ESwitch :modelValue="false" label="暗色模式" />
            </div>
          </div>
        </template>
      </ETabs>
      <p class="text-sm text-muted-foreground mt-2">当前激活：{{ activeTab }}</p>
    </DemoBlock>

    <DemoBlock
      title="带禁用状态"
      description="设置 item 的 disabled: true 禁用指定标签"
      code='const items = [
  { key: "tab1", label: "标签一" },
  { key: "tab3", label: "标签三（禁用）", disabled: true },
]'
    >
      <ETabs v-model="dynamicTab" :items="dynamicItems">
        <template #tab1>
          <div class="p-4 bg-muted/30 rounded-md text-sm">标签一的内容</div>
        </template>
        <template #tab2>
          <div class="p-4 bg-muted/30 rounded-md text-sm">标签二的内容</div>
        </template>
        <template #tab4>
          <div class="p-4 bg-muted/30 rounded-md text-sm">标签四的内容</div>
        </template>
      </ETabs>
    </DemoBlock>
  </div>
</template>
