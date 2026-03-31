<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

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

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础标签页' },
  { id: 'disabled', label: '带禁用状态' },
  { id: 'closable', label: '可关闭标签页' },
  { id: 'vertical', label: '垂直标签页' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'string', default: '-', description: '当前激活标签的 key，支持 v-model' },
  { name: 'items', type: 'TabItem[]', default: '[]', description: '标签项数组，每项包含 key、label、disabled' },
  { name: 'closable', type: 'boolean', default: 'false', description: '是否在每个非禁用标签上显示关闭按钮' },
  { name: 'addable', type: 'boolean', default: 'false', description: '是否在标签栏末尾显示新增按钮' },
  { name: 'tabPosition', type: "'top' | 'bottom' | 'left' | 'right'", default: "'top'", description: '标签栏相对内容区域的位置' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(key: string)', description: '激活标签变更时触发' },
  { name: 'change', params: '(key: string)', description: '切换标签时触发' },
  { name: 'close', params: '(key: string)', description: '点击标签关闭按钮时触发' },
  { name: 'add', params: '()', description: '点击新增按钮时触发' },
]

const slotsData = [
  { name: '[key]', description: '以标签 key 为名的动态插槽，用于渲染对应标签的内容面板' },
]
</script>

<template>
  <ComponentDoc
    title="Tabs 标签页"
    description="标签页组件，支持内容切换、禁用状态、可关闭标签和垂直布局。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于同一页面内不同视图/内容区域的切换，如详情页的「概览 / 详情 / 设置」面板、后台管理的多模块导航等。支持水平和垂直两种布局，以及可关闭 + 可新增的动态标签模式。</p>
    </section>

    <section id="basic">
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
    </section>

    <section id="disabled">
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
    </section>

    <section id="closable">
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
    </section>

    <section id="vertical">
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
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
