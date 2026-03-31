<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'

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
</script>

<template>
  <div class="max-w-4xl">
    <h1 class="text-2xl font-bold mb-2">EDataPage 数据页面</h1>
    <p class="text-muted-foreground mb-6">集成搜索、表格、分页的完整数据列表页组件，传入 fetchFn 即可自动管理数据。</p>

    <DemoBlock
      title="EDataPage 数据页面"
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
  </div>
</template>
