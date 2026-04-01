<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicOpen = ref(false)
const formOpen = ref(false)
const dragOpen = ref(false)
const fullOpen = ref(false)

const formData = ref({ name: '', email: '' })

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic-dialog', label: '基础对话框' },
  { id: 'form-dialog', label: '带表单的对话框' },
  { id: 'draggable-dialog', label: '可拖拽对话框' },
  { id: 'fullscreen-dialog', label: '全屏对话框' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '是否显示对话框（v-model）' },
  { name: 'title', type: 'string', default: '-', description: '对话框标题' },
  { name: 'description', type: 'string', default: '-', description: '对话框描述文字' },
  { name: 'showClose', type: 'boolean', default: 'true', description: '是否显示关闭按钮' },
  { name: 'maxWidth', type: 'string', default: '-', description: '对话框最大宽度（如 "500px"）' },
  { name: 'draggable', type: 'boolean', default: 'false', description: '是否允许拖拽移动' },
  { name: 'closeOnClickModal', type: 'boolean', default: 'true', description: '是否点击遮罩层关闭' },
  { name: 'closeOnPressEscape', type: 'boolean', default: 'true', description: '是否按 Esc 关闭' },
  { name: 'fullscreen', type: 'boolean', default: 'false', description: '是否全屏显示' },
  { name: 'destroyOnClose', type: 'boolean', default: 'false', description: '关闭时是否销毁内容（每次打开重新创建）' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '对话框显示状态变化时触发' },
  { name: 'open', params: '()', description: '对话框打开时触发' },
  { name: 'close', params: '()', description: '对话框关闭时触发' },
]

const slotsData = [
  { name: 'default', description: '对话框主体内容' },
  { name: 'footer', description: '对话框底部操作区域' },
]
</script>

<template>
  <ComponentDoc
    title="Dialog 对话框"
    description="对话框组件，用于需要用户确认的操作、表单录入、信息展示等临时浮层场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Dialog 适用于需要用户确认的操作、表单录入、信息展示等临时浮层场景，支持拖拽、全屏和关闭时销毁内容。</p>
    </section>

    <section id="basic-dialog">
      <DemoBlock
        title="基础对话框"
        description="最简单的确认对话框"
        code='<EDialog v-model:open="open" title="提示" description="你确定要执行此操作吗？">
  <template #footer>
    <EButton variant="outline" @click="open = false">取消</EButton>
    <EButton @click="open = false">确认</EButton>
  </template>
</EDialog>'
      >
        <EButton @click="basicOpen = true">打开基础对话框</EButton>
        <EDialog v-model:open="basicOpen" title="操作确认" description="你确定要执行此操作吗？这将影响所有相关数据。">
          <template #footer>
            <EButton variant="outline" @click="basicOpen = false">取消</EButton>
            <EButton @click="basicOpen = false">确认操作</EButton>
          </template>
        </EDialog>
      </DemoBlock>
    </section>

    <section id="form-dialog">
      <DemoBlock
        title="带表单的对话框"
        description="在对话框中嵌入表单进行数据录入"
      >
        <EButton @click="formOpen = true">打开表单对话框</EButton>
        <EDialog v-model:open="formOpen" title="新建用户" max-width="500px">
          <div class="space-y-4">
            <EFormItem label="姓名">
              <EInput v-model="formData.name" placeholder="请输入姓名" />
            </EFormItem>
            <EFormItem label="邮箱">
              <EInput v-model="formData.email" placeholder="请输入邮箱" />
            </EFormItem>
          </div>
          <template #footer>
            <EButton variant="outline" @click="formOpen = false">取消</EButton>
            <EButton @click="formOpen = false">保存</EButton>
          </template>
        </EDialog>
      </DemoBlock>
    </section>

    <section id="draggable-dialog">
      <DemoBlock
        title="可拖拽对话框"
        description="设置 draggable 允许拖拽移动对话框"
        code='<EDialog :open="dragOpen" title="拖拽我" draggable>内容</EDialog>'
      >
        <EButton @click="dragOpen = true">打开可拖拽对话框</EButton>
        <EDialog v-model:open="dragOpen" title="拖拽我" draggable>
          <p class="text-muted-foreground">按住标题栏可以拖拽移动此对话框。</p>
          <template #footer>
            <EButton variant="outline" @click="dragOpen = false">关闭</EButton>
          </template>
        </EDialog>
      </DemoBlock>
    </section>

    <section id="fullscreen-dialog">
      <DemoBlock
        title="全屏对话框"
        description="设置 fullscreen 使对话框占满全屏"
        code='<EDialog :open="fullOpen" title="全屏" fullscreen>内容</EDialog>'
      >
        <EButton @click="fullOpen = true">打开全屏对话框</EButton>
        <EDialog v-model:open="fullOpen" title="全屏对话框" fullscreen>
          <p class="text-muted-foreground">这是一个全屏对话框，适用于需要大量展示空间的场景。</p>
          <template #footer>
            <EButton variant="outline" @click="fullOpen = false">关闭</EButton>
          </template>
        </EDialog>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Dialog Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Dialog Events</h2>
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Dialog Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
