<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const activeTab = ref('overview')
const dynamicTab = ref('tab1')
const closableTab = ref('tab-1')
const verticalTab = ref('tab-a')

let tabCounter = 3
const closableItems = ref([
  { key: 'tab-1', label: '标签 1' },
  { key: 'tab-2', label: '标签 2' },
  { key: 'tab-3', label: '标签 3' },
])

const handleClose = (key: string) => {
  const idx = closableItems.value.findIndex(item => item.key === key)
  if (idx === -1) return
  closableItems.value.splice(idx, 1)
  if (closableTab.value === key && closableItems.value.length > 0) {
    closableTab.value = closableItems.value[Math.min(idx, closableItems.value.length - 1)].key
  }
}

const handleAdd = () => {
  tabCounter++
  const newKey = `tab-${tabCounter}`
  closableItems.value.push({ key: newKey, label: `标签 ${tabCounter}` })
  closableTab.value = newKey
}

const verticalItems = [
  { key: 'tab-a', label: '用户管理' },
  { key: 'tab-b', label: '角色管理' },
  { key: 'tab-c', label: '权限设置' },
  { key: 'tab-d', label: '系统日志' },
]

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

    <DemoBlock
      title="可关闭标签页"
      description="设置 closable 和 addable 启用标签的关闭与新增"
      code='<ETabs v-model="tab" :items="items" closable addable @close="onClose" @add="onAdd" />'
    >
      <ETabs
        v-model="closableTab"
        :items="closableItems"
        closable
        addable
        @close="handleClose"
        @add="handleAdd"
      >
        <template v-for="item in closableItems" :key="item.key" #[item.key]>
          <div class="p-4 bg-muted/30 rounded-md text-sm">{{ item.label }} 的内容区域</div>
        </template>
      </ETabs>
    </DemoBlock>

    <DemoBlock
      title="垂直标签页"
      description="设置 tab-position=&quot;left&quot; 实现垂直布局"
      code='<ETabs v-model="tab" :items="items" tab-position="left" />'
    >
      <ETabs v-model="verticalTab" :items="verticalItems" tab-position="left">
        <template #tab-a>
          <div class="p-4 bg-muted/30 rounded-md text-sm">用户管理页面内容</div>
        </template>
        <template #tab-b>
          <div class="p-4 bg-muted/30 rounded-md text-sm">角色管理页面内容</div>
        </template>
        <template #tab-c>
          <div class="p-4 bg-muted/30 rounded-md text-sm">权限设置页面内容</div>
        </template>
        <template #tab-d>
          <div class="p-4 bg-muted/30 rounded-md text-sm">系统日志页面内容</div>
        </template>
      </ETabs>
    </DemoBlock>
  </div>
</template>
