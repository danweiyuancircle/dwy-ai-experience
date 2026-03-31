<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const basicOpen = ref(false)
const formOpen = ref(false)
const dragOpen = ref(false)
const fullOpen = ref(false)
const drawerRight = ref(false)
const drawerLeft = ref(false)
const drawerTop = ref(false)
const drawerBottom = ref(false)

const formData = ref({ name: '', email: '' })
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Dialog & Drawer</h1>
    <p class="text-muted-foreground mb-6">对话框和抽屉组件，用于临时内容展示或操作面板。</p>

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
  </div>
</template>
