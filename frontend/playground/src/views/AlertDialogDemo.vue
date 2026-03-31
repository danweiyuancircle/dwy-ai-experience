<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicOpen = ref(false)
const dangerOpen = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础确认' },
  { id: 'danger', label: '危险确认' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '控制对话框的显示/隐藏' },
  { name: 'title', type: 'string', description: '对话框标题' },
  { name: 'description', type: 'string', description: '对话框描述内容' },
  { name: 'confirmText', type: 'string', default: "'确认'", description: '确认按钮文字' },
  { name: 'cancelText', type: 'string', default: "'取消'", description: '取消按钮文字' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '对话框打开/关闭时触发' },
  { name: 'confirm', params: '()', description: '点击确认按钮时触发' },
  { name: 'cancel', params: '()', description: '点击取消按钮时触发' },
]

const slotsData = [
  { name: 'trigger', description: '触发器内容，点击后打开对话框' },
  { name: 'title', description: '自定义标题区域' },
  { name: 'description', description: '自定义描述区域' },
  { name: 'default', description: '对话框主体内容' },
  { name: 'footer', description: '自定义底部按钮区域' },
]
</script>

<template>
  <ComponentDoc
    title="AlertDialog 警告对话框"
    description="用于需要用户明确确认的操作，如删除、退出等不可撤销的动作。不同于普通 Dialog，AlertDialog 必须通过按钮交互才能关闭。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于删除记录、退出编辑、清空数据等需要二次确认的危险操作。与普通 Dialog 的区别在于：用户无法通过点击遮罩层或按 Escape 关闭对话框，必须主动点击确认或取消按钮。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础确认"
        description="默认的确认对话框，包含标题、描述和确认/取消按钮"
        code='<EAlertDialog
  v-model:open="basicOpen"
  title="确认提交"
  description="提交后数据将被保存，确认继续？"
  @confirm="handleConfirm"
>
  <template #trigger>
    <EButton>打开确认对话框</EButton>
  </template>
</EAlertDialog>'
      >
        <EAlertDialog
          v-model:open="basicOpen"
          title="确认提交"
          description="提交后数据将被保存，确认继续？"
        >
          <template #trigger>
            <EButton>打开确认对话框</EButton>
          </template>
        </EAlertDialog>
      </DemoBlock>
    </section>

    <section id="danger">
      <DemoBlock
        title="危险确认"
        description="自定义确认按钮文字，突出危险操作的提示"
        code='<EAlertDialog
  v-model:open="dangerOpen"
  title="确认删除"
  description="此操作将永久删除该记录，且无法恢复。"
  confirmText="删除"
  cancelText="放弃"
>
  <template #trigger>
    <EButton variant="destructive">删除记录</EButton>
  </template>
</EAlertDialog>'
      >
        <EAlertDialog
          v-model:open="dangerOpen"
          title="确认删除"
          description="此操作将永久删除该记录，且无法恢复。"
          confirmText="删除"
          cancelText="放弃"
        >
          <template #trigger>
            <EButton variant="destructive">删除记录</EButton>
          </template>
        </EAlertDialog>
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
