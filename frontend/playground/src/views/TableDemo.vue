<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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

function getRowClassName({ row }: { row: any }) {
  if (row.status === '离职') return 'bg-red-50 dark:bg-red-950/20'
  if (row.status === '休假') return 'bg-yellow-50 dark:bg-yellow-950/20'
  return ''
}
</script>

<template>
  <div class="max-w-4xl">
    <h1 class="text-2xl font-bold mb-2">Table 表格</h1>
    <p class="text-muted-foreground mb-6">数据表格组件，支持排序、行选择、条纹/边框样式、自定义渲染等。</p>

    <DemoBlock
      title="基础表格"
      description="最简单的数据表格"
      code='<ETable :data="data" :columns="columns" />'
    >
      <ETable :data="data" :columns="columns" />
    </DemoBlock>

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

    <DemoBlock
      title="行选择"
      description="设置 selectable 启用多行选择"
      code='<ETable :data="data" :columns="columns" selectable v-model:selectedKeys="selectedKeys" />'
    >
      <ETable :data="data" :columns="columns" :selectable="true" v-model:selectedKeys="selectedKeys" row-key="id" />
      <p class="text-sm text-muted-foreground mt-2">已选：{{ selectedKeys.length > 0 ? selectedKeys.join(', ') : '无' }}</p>
    </DemoBlock>

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

    <DemoBlock
      title="空状态"
      description="data 为空时显示 emptyText"
      code='<ETable :data="[]" :columns="columns" emptyText="暂无数据" />'
    >
      <ETable :data="[]" :columns="columns" empty-text="暂无数据，请添加记录" />
    </DemoBlock>

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

    <DemoBlock
      title="合计行"
      description="设置 show-summary 在表格底部显示合计行"
      code='<ETable :data="data" :columns="columns" show-summary />'
    >
      <ETable :data="data" :columns="summaryColumns" show-summary row-key="id" />
    </DemoBlock>

    <DemoBlock
      title="自定义行样式"
      description="通过 :row-class-name 函数根据条件为行添加自定义样式"
      code='<ETable :data="data" :columns="columns" :row-class-name="getRowClassName" />'
    >
      <ETable :data="data" :columns="columns" :row-class-name="getRowClassName" row-key="id" />
      <p class="text-xs text-muted-foreground mt-2">离职行标红背景，休假行标黄背景</p>
    </DemoBlock>
  </div>
</template>
