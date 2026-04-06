<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const loading = ref(false)

const columns = [
  { key: 'name', title: '姓名', sortable: true },
  { key: 'age', title: '年龄', sortable: true },
  { key: 'role', title: '角色' },
  { key: 'status', title: '状态' },
]

const data = [
  { id: 1, name: '张三', age: 28, role: '管理员', status: '在职' },
  { id: 2, name: '李四', age: 35, role: '编辑员', status: '在职' },
  { id: 3, name: '王五', age: 22, role: '访客', status: '离职' },
  { id: 4, name: '赵六', age: 41, role: '管理员', status: '在职' },
  { id: 5, name: '孙七', age: 29, role: '编辑员', status: '休假' },
]

const selectedKeys = ref<(string | number)[]>([])
const striped = ref(false)
const bordered = ref(false)

function toggleLoading() {
  loading.value = true
  setTimeout(() => (loading.value = false), 1500)
}

const expandColumns = [
  { key: 'name', title: '姓名' },
  { key: 'age', title: '年龄' },
  { key: 'role', title: '角色' },
]

const summaryColumns = [
  { key: 'name', title: '姓名' },
  { key: 'age', title: '年龄', sortable: true },
  { key: 'role', title: '角色' },
  { key: 'status', title: '状态' },
]

function getRowClassName(row: any) {
  if (row.status === '离职') return 'bg-red-50 dark:bg-red-950/20'
  if (row.status === '休假') return 'bg-yellow-50 dark:bg-yellow-950/20'
  return ''
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础表格' },
  { id: 'striped', label: '条纹与边框' },
  { id: 'selection', label: '行选择' },
  { id: 'loading', label: 'Loading 状态' },
  { id: 'empty', label: '空状态' },
  { id: 'custom-cell', label: '自定义单元格' },
  { id: 'expand', label: '展开行' },
  { id: 'summary', label: '合计行' },
  { id: 'row-class', label: '自定义行样式' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'data', type: "Record<string, any>[]", default: '[]', description: '表格数据源' },
  { name: 'columns', type: 'TableColumn[]', default: '[]', description: '列配置数组' },
  { name: 'loading', type: 'boolean', default: 'false', description: '是否显示加载覆盖层' },
  { name: 'rowKey', type: 'string', default: "'id'", description: '行数据唯一标识字段名' },
  { name: 'striped', type: 'boolean', default: 'false', description: '是否显示斑马纹' },
  { name: 'bordered', type: 'boolean', default: 'false', description: '是否显示完整边框' },
  { name: 'emptyText', type: 'string', default: '-', description: '数据为空时的提示文案' },
  { name: 'selectable', type: 'boolean', default: 'false', description: '是否启用多行选择' },
  { name: 'selectedKeys', type: '(string | number)[]', default: '[]', description: '当前选中的行 key 数组（v-model）' },
  { name: 'expandable', type: 'boolean', default: 'false', description: '是否启用行展开功能' },
  { name: 'expandedRowKeys', type: '(string | number)[]', default: '[]', description: '当前展开的行 key 数组（v-model）' },
  { name: 'rowClassName', type: 'string | ((row, index) => string)', default: '-', description: '自定义行 CSS 类名，支持函数动态返回' },
  { name: 'showSummary', type: 'boolean', default: 'false', description: '是否显示底部合计行' },
  { name: 'summaryMethod', type: '(data, columns) => (string | number)[]', default: '-', description: '自定义合计行计算方法' },
  { name: 'virtual', type: 'boolean', default: 'false', description: '是否启用虚拟滚动（大数据量）' },
  { name: 'virtualRowHeight', type: 'number', default: '-', description: '虚拟滚动时的行高（px）' },
  { name: 'resizable', type: 'boolean', default: 'false', description: '是否允许拖拽调整列宽' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'row-click', params: '(row: Record<string, any>, index: number)', description: '点击行时触发' },
  { name: 'update:selectedKeys', params: '(keys: (string | number)[])', description: '选中行变化时触发' },
  { name: 'update:expandedRowKeys', params: '(keys: (string | number)[])', description: '展开行变化时触发' },
  { name: 'sort', params: "(key: string, direction: 'asc' | 'desc' | null)", description: '点击排序时触发' },
]

const slotsData = [
  { name: 'cell-{key}', description: '自定义指定列的单元格渲染，参数 { value, row, index }' },
  { name: 'expand', description: '展开行内容插槽，参数 { row }' },
  { name: 'empty', description: '自定义空状态内容' },
]
</script>

<template>
  <ComponentDoc
    title="Table 表格"
    description="数据表格组件，支持排序、行选择、条纹/边框样式、自定义渲染等。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于展示结构化的数据集合，如用户列表、订单记录、日志信息等。支持列排序、多行选择、行展开、合计行、条纹/边框切换、自定义单元格渲染等常见表格需求。通过插槽机制可灵活定制任意列的展示内容。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础表格"
        description="最简单的数据表格"
        code='<ETable :data="data" :columns="columns" />'
      >
        <ETable :data="data" :columns="columns" />
      </DemoBlock>
    </section>

    <section id="striped">
      <DemoBlock
        title="条纹与边框"
        description="通过 striped 和 bordered 控制样式"
      >
        <div class="flex gap-4 mb-4">
          <ESwitch v-model="striped" label="条纹样式" />
          <ESwitch v-model="bordered" label="边框样式" />
        </div>
        <ETable :data="data" :columns="columns" :striped="striped" :bordered="bordered" />
      </DemoBlock>
    </section>

    <section id="selection">
      <DemoBlock
        title="行选择"
        description="设置 selectable 启用多行选择"
        code='<ETable :data="data" :columns="columns" selectable v-model:selectedKeys="selectedKeys" />'
      >
        <ETable :data="data" :columns="columns" :selectable="true" v-model:selectedKeys="selectedKeys" row-key="id" />
        <p class="text-sm text-muted-foreground mt-2">已选：{{ selectedKeys.length > 0 ? selectedKeys.join(', ') : '无' }}</p>
      </DemoBlock>
    </section>

    <section id="loading">
      <DemoBlock
        title="Loading 状态"
        description="设置 loading 显示加载覆盖层"
        code='<ETable :data="data" :columns="columns" :loading="loading" />'
      >
        <div class="mb-4">
          <EButton @click="toggleLoading">触发 1.5 秒 Loading</EButton>
        </div>
        <ETable :data="data" :columns="columns" :loading="loading" />
      </DemoBlock>
    </section>

    <section id="empty">
      <DemoBlock
        title="空状态"
        description="data 为空时显示 emptyText"
        code='<ETable :data="[]" :columns="columns" emptyText="暂无数据" />'
      >
        <ETable :data="[]" :columns="columns" empty-text="暂无数据，请添加记录" />
      </DemoBlock>
    </section>

    <section id="custom-cell">
      <DemoBlock
        title="自定义单元格（插槽）"
        description="通过 #cell-{key} 插槽自定义列渲染"
        code='<ETable :data="data" :columns="columns">
  <template #cell-status="{ value }">
    <EBadge :variant="value === &apos;在职&apos; ? &apos;default&apos; : &apos;outline&apos;">{{ value }}</EBadge>
  </template>
</ETable>'
      >
        <ETable :data="data" :columns="columns">
          <template #cell-status="{ value }">
            <EBadge :variant="value === '在职' ? 'default' : value === '休假' ? 'secondary' : 'outline'">
              {{ value }}
            </EBadge>
          </template>
          <template #cell-role="{ value }">
            <span :class="value === '管理员' ? 'text-primary font-medium' : 'text-muted-foreground'">
              {{ value }}
            </span>
          </template>
        </ETable>
      </DemoBlock>
    </section>

    <section id="expand">
      <DemoBlock
        title="展开行"
        description="设置 expandable 启用行展开，通过 #expand 插槽自定义展开内容"
        code='<ETable :data="data" :columns="columns" expandable>
  <template #expand="{ row }">
    <pre>{{ JSON.stringify(row, null, 2) }}</pre>
  </template>
</ETable>'
      >
        <ETable :data="data" :columns="expandColumns" expandable row-key="id">
          <template #expand="{ row }">
            <div class="p-4 bg-muted/30">
              <p class="text-sm font-medium mb-2">行详情</p>
              <pre class="text-xs text-muted-foreground">{{ JSON.stringify(row, null, 2) }}</pre>
            </div>
          </template>
        </ETable>
      </DemoBlock>
    </section>

    <section id="summary">
      <DemoBlock
        title="合计行"
        description="设置 show-summary 在表格底部显示合计行"
        code='<ETable :data="data" :columns="columns" show-summary />'
      >
        <ETable :data="data" :columns="summaryColumns" show-summary row-key="id" />
      </DemoBlock>
    </section>

    <section id="row-class">
      <DemoBlock
        title="自定义行样式"
        description="通过 :row-class-name 函数根据条件为行添加自定义样式"
        code='<ETable :data="data" :columns="columns" :row-class-name="getRowClassName" />'
      >
        <ETable :data="data" :columns="columns" :row-class-name="getRowClassName" row-key="id" />
        <p class="text-xs text-muted-foreground mt-2">离职行标红背景，休假行标黄背景</p>
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
