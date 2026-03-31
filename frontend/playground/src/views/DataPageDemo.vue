<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'

const columns = [
  { key: 'id', title: 'ID' },
  { key: 'name', title: '姓名' },
  { key: 'role', title: '角色' },
  { key: 'status', title: '状态' },
]

const mockUsers = [
  { id: 1, name: '张三', role: '管理员', status: '在职' },
  { id: 2, name: '李四', role: '编辑员', status: '在职' },
  { id: 3, name: '王五', role: '访客', status: '离职' },
  { id: 4, name: '赵六', role: '管理员', status: '在职' },
  { id: 5, name: '孙七', role: '编辑员', status: '休假' },
  { id: 6, name: '周八', role: '访客', status: '在职' },
  { id: 7, name: '吴九', role: '编辑员', status: '在职' },
  { id: 8, name: '郑十', role: '管理员', status: '离职' },
]

async function fetchUsers({ page, pageSize, keyword }: { page: number; pageSize: number; keyword?: string }) {
  await new Promise(resolve => setTimeout(resolve, 500))
  let filtered = mockUsers
  if (keyword) {
    filtered = mockUsers.filter(u => u.name.includes(keyword) || u.role.includes(keyword))
  }
  const start = (page - 1) * pageSize
  return {
    items: filtered.slice(start, start + pageSize),
    total: filtered.length,
  }
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'columns', type: 'TableColumn[]', description: '表格列定义（{ key, title, ... }）' },
  { name: 'fetchFn', type: '(params: FetchParams) => Promise<FetchResult>', description: '数据获取函数，接收 { page, pageSize, keyword }，返回 { items, total }' },
  { name: 'searchable', type: 'boolean', default: 'true', description: '是否显示搜索栏' },
  { name: 'pageSize', type: 'number', default: '10', description: '每页条数' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]
</script>

<template>
  <ComponentDoc
    title="DataPage 数据页面"
    description="集成搜索、表格、分页的完整数据列表页组件，传入 fetchFn 即可自动管理数据加载和分页。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于后台管理系统中的数据列表页面。只需提供列定义和数据获取函数，组件自动处理搜索、分页、加载状态。fetchFn 接收 { page, pageSize, keyword } 参数，返回 { items, total } 结构。组件内部自动管理翻页和关键词搜索。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="集成搜索、表格、分页的完整数据列表页组件，传入 fetchFn 即可自动管理数据"
        code='<EDataPage
  :columns="columns"
  :fetchFn="fetchUsers"
  :searchable="true"
  :pageSize="5"
/>'
      >
        <EDataPage
          :columns="columns"
          :fetch-fn="fetchUsers"
          :searchable="true"
          :page-size="5"
        />
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Slots</h2>
      <p class="text-sm text-muted-foreground">该组件无自定义插槽。</p>
    </section>
  </ComponentDoc>
</template>
