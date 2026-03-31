<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

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

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '对话框是否打开（支持 v-model:open）' },
  { name: 'title', type: 'string', description: '对话框标题' },
  { name: 'size', type: 'string', description: '对话框最大宽度（传入 CSS 值，如 "600px"）' },
  { name: 'loading', type: 'boolean', default: 'false', description: '加载状态，禁用确认和取消按钮' },
  { name: 'confirmText', type: 'string', default: "'确认'", description: '确认按钮文字' },
  { name: 'cancelText', type: 'string', default: "'取消'", description: '取消按钮文字' },
  { name: 'showClose', type: 'boolean', default: 'true', description: '是否显示关闭按钮（loading 时自动隐藏）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '打开/关闭状态变化时触发' },
  { name: 'confirm', params: '()', description: '点击确认按钮时触发' },
  { name: 'cancel', params: '()', description: '点击取消按钮时触发' },
]

const slotsData = [
  { name: 'default', description: '对话框主体内容（表单区域）' },
  { name: 'trigger', description: '触发器插槽，点击后打开对话框' },
  { name: 'footer', description: '自定义底部按钮区域（默认为取消+确认按钮）' },
]
</script>

<template>
  <ComponentDoc
    title="FormDialog 表单对话框"
    description="内置表单的对话框，支持 loading 状态和确认/取消回调，适合创建和编辑场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于新建/编辑实体的弹窗表单场景。内置确认和取消按钮，支持 loading 状态防止重复提交。通过 v-model:open 控制开关状态，confirm 和 cancel 事件处理业务逻辑。底部按钮区域可通过 footer 插槽完全自定义。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
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
