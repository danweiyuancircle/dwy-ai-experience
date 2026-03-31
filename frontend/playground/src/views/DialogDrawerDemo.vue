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
const drawerRight = ref(false)
const drawerLeft = ref(false)
const drawerTop = ref(false)
const drawerBottom = ref(false)

const formData = ref({ name: '', email: '' })

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic-dialog', label: '基础对话框' },
  { id: 'form-dialog', label: '带表单的对话框' },
  { id: 'draggable-dialog', label: '可拖拽对话框' },
  { id: 'fullscreen-dialog', label: '全屏对话框' },
  { id: 'drawer-right', label: '右侧抽屉' },
  { id: 'drawer-directions', label: '多方向抽屉' },
  { id: 'dialog-props', label: 'Dialog Props' },
  { id: 'dialog-events', label: 'Dialog Events' },
  { id: 'dialog-slots', label: 'Dialog Slots' },
  { id: 'drawer-props', label: 'Drawer Props' },
  { id: 'drawer-events', label: 'Drawer Events' },
  { id: 'drawer-slots', label: 'Drawer Slots' },
]

const dialogPropsData = [
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

const dialogEventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '对话框显示状态变化时触发' },
  { name: 'open', params: '()', description: '对话框打开时触发' },
  { name: 'close', params: '()', description: '对话框关闭时触发' },
]

const dialogSlotsData = [
  { name: 'default', description: '对话框主体内容' },
  { name: 'footer', description: '对话框底部操作区域' },
]

const drawerPropsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '是否显示抽屉（v-model）' },
  { name: 'title', type: 'string', default: '-', description: '抽屉标题' },
  { name: 'description', type: 'string', default: '-', description: '抽屉描述文字' },
  { name: 'direction', type: "'top' | 'right' | 'bottom' | 'left'", default: "'right'", description: '抽屉滑出方向' },
  { name: 'showClose', type: 'boolean', default: 'true', description: '是否显示关闭按钮' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const drawerEventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '抽屉显示状态变化时触发' },
  { name: 'close', params: '()', description: '抽屉关闭时触发' },
]

const drawerSlotsData = [
  { name: 'default', description: '抽屉主体内容' },
]
</script>

<template>
  <ComponentDoc
    title="Dialog & Drawer"
    description="对话框和抽屉组件，用于临时内容展示或操作面板。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Dialog 适用于需要用户确认的操作、表单录入、信息展示等临时浮层场景，支持拖拽、全屏和关闭时销毁内容。Drawer 适用于详情面板、筛选侧栏、设置面板等从屏幕边缘滑入的场景，支持上下左右四个方向。</p>
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

    <section id="drawer-right">
      <DemoBlock
        title="右侧抽屉"
        description="从右侧滑入的抽屉（默认方向）"
        code='<EDrawer v-model:open="open" title="用户详情" direction="right">
  内容区域
</EDrawer>'
      >
        <EButton @click="drawerRight = true">右侧抽屉</EButton>
        <EDrawer v-model:open="drawerRight" title="用户详情" direction="right">
          <div class="p-4 space-y-3">
            <p class="text-muted-foreground">这里是抽屉的内容区域，可以放置任何内容。</p>
            <EDescriptions :items="[
              { label: '姓名', value: '张三' },
              { label: '邮箱', value: 'zhangsan@example.com' },
              { label: '角色', value: '管理员' },
              { label: '状态', value: '在职' },
            ]" />
          </div>
        </EDrawer>
      </DemoBlock>
    </section>

    <section id="drawer-directions">
      <DemoBlock
        title="多方向抽屉"
        description="支持 top / right / bottom / left 四个方向"
      >
        <div class="flex flex-wrap gap-2">
          <EButton variant="outline" @click="drawerLeft = true">左侧</EButton>
          <EButton variant="outline" @click="drawerRight = true">右侧</EButton>
          <EButton variant="outline" @click="drawerTop = true">顶部</EButton>
          <EButton variant="outline" @click="drawerBottom = true">底部</EButton>
        </div>
        <EDrawer v-model:open="drawerLeft" title="左侧抽屉" direction="left">
          <div class="p-4"><p class="text-muted-foreground">左侧抽屉内容</p></div>
        </EDrawer>
        <EDrawer v-model:open="drawerTop" title="顶部抽屉" direction="top">
          <div class="p-4"><p class="text-muted-foreground">顶部抽屉内容</p></div>
        </EDrawer>
        <EDrawer v-model:open="drawerBottom" title="底部抽屉" direction="bottom">
          <div class="p-4"><p class="text-muted-foreground">底部抽屉内容</p></div>
        </EDrawer>
      </DemoBlock>
    </section>

    <section id="dialog-props">
      <h2 class="text-lg font-semibold mb-3">Dialog Props</h2>
      <PropsTable :data="dialogPropsData" />
    </section>

    <section id="dialog-events">
      <h2 class="text-lg font-semibold mb-3">Dialog Events</h2>
      <EventsTable :data="dialogEventsData" />
    </section>

    <section id="dialog-slots">
      <h2 class="text-lg font-semibold mb-3">Dialog Slots</h2>
      <SlotsTable :data="dialogSlotsData" />
    </section>

    <section id="drawer-props">
      <h2 class="text-lg font-semibold mb-3">Drawer Props</h2>
      <PropsTable :data="drawerPropsData" />
    </section>

    <section id="drawer-events">
      <h2 class="text-lg font-semibold mb-3">Drawer Events</h2>
      <EventsTable :data="drawerEventsData" />
    </section>

    <section id="drawer-slots">
      <h2 class="text-lg font-semibold mb-3">Drawer Slots</h2>
      <SlotsTable :data="drawerSlotsData" />
    </section>
  </ComponentDoc>
</template>
