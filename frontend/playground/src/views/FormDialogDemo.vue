<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '编辑员', value: 'editor' },
  { label: '访客', value: 'guest' },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">EFormDialog 表单对话框</h1>
    <p class="text-muted-foreground mb-6">内置表单的对话框，支持 loading 状态和确认/取消回调。</p>

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
  </div>
</template>
