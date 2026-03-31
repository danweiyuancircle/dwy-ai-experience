<script setup lang="ts">
import { ref, computed } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const lastClickedRow = ref<Record<string, string | number> | null>(null)
const isLoading = ref(false)

function toggleLoading() {
  isLoading.value = true
  setTimeout(() => (isLoading.value = false), 2000)
}

const columns = [
  { key: 'id', title: 'ID', width: 80, align: 'center' as const },
  { key: 'name', title: '姓名', width: 120 },
  { key: 'email', title: '邮箱', width: 220 },
  { key: 'department', title: '部门', width: 120 },
  { key: 'role', title: '职位', width: 120 },
  { key: 'salary', title: '薪资', width: 100, align: 'right' as const },
  { key: 'city', title: '城市', width: 100 },
  { key: 'status', title: '状态', width: 80, align: 'center' as const },
]

const departments = ['技术部', '产品部', '设计部', '市场部', '运营部', '人力资源部', '财务部']
const roles = ['工程师', '高级工程师', '产品经理', '设计师', '运营经理', '分析师', '总监', '实习生']
const cities = ['北京', '上海', '深圳', '杭州', '成都', '广州', '南京', '武汉']
const statuses = ['在职', '离职', '休假']
const lastNames = ['张', '李', '王', '刘', '陈', '杨', '赵', '周', '吴', '孙']
const firstNames = ['伟', '芳', '娜', '敏', '静', '强', '磊', '洋', '勇', '艳', '杰', '秀英', '明', '丽']

function generateMockData(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `${lastNames[i % lastNames.length]}${firstNames[i % firstNames.length]}`,
    email: `user${i + 1}@example.com`,
    department: departments[i % departments.length],
    role: roles[i % roles.length],
    salary: (Math.floor(Math.random() * 30 + 10) * 1000).toLocaleString(),
    city: cities[i % cities.length],
    status: statuses[i % statuses.length],
  }))
}

const tableData = computed(() => generateMockData(1000))

function handleRowClick(row: Record<string, string | number>) {
  lastClickedRow.value = row
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'large-dataset', label: '大数据量' },
  { id: 'loading', label: '加载状态' },
  { id: 'empty', label: '空数据' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'columns', type: 'VirtualTableColumn[]', default: '[]', description: '表格列定义' },
  { name: 'data', type: 'Record<string, any>[]', default: '[]', description: '表格数据源' },
  { name: 'height', type: 'number', default: '400', description: '表格容器高度（px）' },
  { name: 'estimateRowHeight', type: 'number', default: '40', description: '预估行高（px），用于虚拟滚动计算' },
  { name: 'rowKey', type: 'string', default: "'id'", description: '行数据唯一标识字段名' },
  { name: 'loading', type: 'boolean', default: 'false', description: '是否显示加载遮罩' },
  { name: 'emptyText', type: 'string', default: "'No data'", description: '空数据时的提示文字' },
]

const eventsData = [
  { name: 'row-click', params: '(row: Record<string, any>, index: number)', description: '点击行时触发' },
]

const slotsData = [
  { name: 'cell-{key}', props: '{ row, value, index }', description: '自定义单元格内容，key 为列的 key 值' },
]
</script>

<template>
  <ComponentDoc
    title="VirtualTable 虚拟表格"
    description="高性能虚拟滚动表格，适用于展示大数据量列表，支持自定义列、行点击事件和加载状态。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">当数据量达到数百甚至上千行时，普通表格会导致 DOM 节点过多、渲染卡顿。VirtualTable 通过虚拟滚动技术，只渲染可视区域内的行，大幅提升渲染性能。适用于日志查看、数据导出预览、大批量人员列表等场景。</p>
    </section>

    <section id="large-dataset">
      <DemoBlock
        title="大数据量（1000 行）"
        description="生成 1000 条模拟数据，滚动时只渲染可见行"
        code='<EVirtualTable
  :columns="columns"
  :data="tableData"
  :height="400"
  row-key="id"
  @row-click="handleRowClick"
/>'
      >
        <div class="space-y-3">
          <EVirtualTable
            :columns="columns"
            :data="tableData"
            :height="400"
            row-key="id"
            @row-click="handleRowClick"
          />
          <p v-if="lastClickedRow" class="text-sm text-muted-foreground">
            点击了：{{ lastClickedRow.name }} - {{ lastClickedRow.department }} - {{ lastClickedRow.role }}
          </p>
        </div>
      </DemoBlock>
    </section>

    <section id="loading">
      <DemoBlock
        title="加载状态"
        description="设置 loading 后表格上方显示加载遮罩"
        code='<EVirtualTable :columns="columns" :data="data" :loading="true" />'
      >
        <div class="space-y-3">
          <EButton variant="outline" @click="toggleLoading">
            {{ isLoading ? '加载中...' : '模拟加载 2 秒' }}
          </EButton>
          <EVirtualTable
            :columns="columns"
            :data="tableData.slice(0, 20)"
            :height="300"
            :loading="isLoading"
            row-key="id"
          />
        </div>
      </DemoBlock>
    </section>

    <section id="empty">
      <DemoBlock
        title="空数据"
        description="无数据时显示空状态提示"
        code='<EVirtualTable :columns="columns" :data="[]" empty-text="暂无数据" />'
      >
        <EVirtualTable
          :columns="columns"
          :data="[]"
          :height="200"
          empty-text="暂无数据"
        />
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
