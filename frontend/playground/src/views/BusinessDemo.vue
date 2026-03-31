<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

// EFormDialog demo
const formDialogOpen = ref(false)
const formDialogLoading = ref(false)
const formData = ref({ name: '', email: '', role: '' })

function handleFormConfirm() {
  formDialogLoading.value = true
  setTimeout(() => {
    formDialogLoading.value = false
    formDialogOpen.value = false
  }, 1500)
}

// EConfirmDialog demo
const confirmOpen = ref(false)
const confirmWarningOpen = ref(false)
const confirmErrorOpen = ref(false)
const confirmResult = ref('')

// EDataPage demo
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

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '编辑员', value: 'editor' },
  { label: '访客', value: 'guest' },
]
</script>

<template>
  <div class="max-w-4xl">
    <h1 class="text-2xl font-bold mb-2">业务组件</h1>
    <p class="text-muted-foreground mb-6">专为企业中后台场景设计的高阶组件，包含 EFormDialog、EConfirmDialog、EDataPage 等。</p>

    <DemoBlock
      title="EFormDialog 表单对话框"
      description="内置表单的对话框，支持 loading 状态和确认/取消回调"
      code='<EFormDialog v-model:open="open" title="新建用户" :loading="loading" @confirm="handleConfirm">
  <EFormItem label="姓名">
    <EInput v-model="data.name" />
  </EFormItem>
</EFormDialog>'
    >
      <EButton @click="formDialogOpen = true">打开表单对话框</EButton>

      <EFormDialog
        v-model:open="formDialogOpen"
        title="新建用户"
        :loading="formDialogLoading"
        confirm-text="保存"
        @confirm="handleFormConfirm"
        @cancel="formDialogOpen = false"
      >
        <div class="space-y-4">
          <EFormItem label="姓名">
            <EInput v-model="formData.name" placeholder="请输入姓名" />
          </EFormItem>
          <EFormItem label="邮箱">
            <EInput v-model="formData.email" placeholder="请输入邮箱" />
          </EFormItem>
          <EFormItem label="角色">
            <ESelect v-model="formData.role" :options="roleOptions" placeholder="请选择角色" class="w-full" />
          </EFormItem>
        </div>
      </EFormDialog>
    </DemoBlock>

    <DemoBlock
      title="EConfirmDialog 确认对话框"
      description="支持 info / warning / error 三种危险等级"
      code='<EConfirmDialog
  v-model:open="open"
  type="warning"
  title="确认删除"
  message="此操作不可逆，确定要删除吗？"
  @confirm="handleConfirm"
/>'
    >
      <div class="flex flex-wrap gap-3">
        <EButton variant="outline" @click="confirmOpen = true">信息确认</EButton>
        <EButton variant="secondary" @click="confirmWarningOpen = true">警告确认</EButton>
        <EButton variant="destructive" @click="confirmErrorOpen = true">危险确认</EButton>
      </div>
      <p v-if="confirmResult" class="text-sm mt-2 text-muted-foreground">操作结果：{{ confirmResult }}</p>

      <EConfirmDialog
        v-model:open="confirmOpen"
        type="info"
        title="确认操作"
        message="您确定要执行此操作吗？这将影响所有相关数据。"
        @confirm="() => { confirmResult = '点击了确认（info）'; confirmOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmOpen = false }"
      />
      <EConfirmDialog
        v-model:open="confirmWarningOpen"
        type="warning"
        title="注意"
        message="此操作将清空所有缓存数据，确定继续吗？"
        confirm-text="继续"
        @confirm="() => { confirmResult = '点击了继续（warning）'; confirmWarningOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmWarningOpen = false }"
      />
      <EConfirmDialog
        v-model:open="confirmErrorOpen"
        type="error"
        title="危险操作"
        message="此操作将永久删除所有数据，无法恢复。请确认您已知晓此风险。"
        confirm-text="我已知晓，继续删除"
        cancel-text="取消"
        @confirm="() => { confirmResult = '点击了删除（error）'; confirmErrorOpen = false }"
        @cancel="() => { confirmResult = '点击了取消'; confirmErrorOpen = false }"
      />
    </DemoBlock>

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
