<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const popoverOpen = ref(false)
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Tooltip & Popover</h1>
    <p class="text-muted-foreground mb-6">Tooltip 用于简短文字提示，Popover 用于富内容气泡卡片。</p>

    <DemoBlock
      title="Tooltip 基础用法"
      description="悬停时显示简短提示文字"
      code='<ETooltip content="这是一条提示信息">
  <EButton>悬停查看提示</EButton>
</ETooltip>'
    >
      <div class="flex flex-wrap gap-3">
        <ETooltip content="这是顶部提示" side="top">
          <EButton variant="outline">顶部 Top</EButton>
        </ETooltip>
        <ETooltip content="这是底部提示" side="bottom">
          <EButton variant="outline">底部 Bottom</EButton>
        </ETooltip>
        <ETooltip content="这是左侧提示" side="left">
          <EButton variant="outline">左侧 Left</EButton>
        </ETooltip>
        <ETooltip content="这是右侧提示" side="right">
          <EButton variant="outline">右侧 Right</EButton>
        </ETooltip>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Tooltip 延迟"
      description="通过 delayDuration 控制显示延迟（毫秒）"
      code='<ETooltip content="延迟 500ms 显示" :delayDuration="500">
  <EButton>延迟 Tooltip</EButton>
</ETooltip>'
    >
      <div class="flex gap-3">
        <ETooltip content="即时显示（0ms）" :delayDuration="0">
          <EButton variant="outline" size="sm">即时</EButton>
        </ETooltip>
        <ETooltip content="延迟 300ms 显示" :delayDuration="300">
          <EButton variant="outline" size="sm">300ms 延迟</EButton>
        </ETooltip>
        <ETooltip content="延迟 800ms 显示" :delayDuration="800">
          <EButton variant="outline" size="sm">800ms 延迟</EButton>
        </ETooltip>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Popover 基础用法"
      description="点击触发，显示富内容气泡卡片"
      code='<EPopover>
  <template #trigger>
    <EButton>打开 Popover</EButton>
  </template>
  <div class="p-3">Popover 内容</div>
</EPopover>'
    >
      <EPopover>
        <template #trigger>
          <EButton variant="outline">点击打开 Popover</EButton>
        </template>
        <div class="p-3 min-w-[200px]">
          <h4 class="font-semibold mb-2">用户信息</h4>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-muted-foreground">姓名</span>
              <span>张三</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">角色</span>
              <span>管理员</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">状态</span>
              <EBadge variant="default">在线</EBadge>
            </div>
          </div>
          <div class="mt-3 pt-3 border-t flex gap-2">
            <EButton size="sm" class="flex-1">查看详情</EButton>
            <EButton size="sm" variant="outline">消息</EButton>
          </div>
        </div>
      </EPopover>
    </DemoBlock>

    <DemoBlock
      title="Popover 多方向"
      description="通过 side 和 align 控制弹出位置"
    >
      <div class="flex flex-wrap gap-3">
        <EPopover side="top">
          <template #trigger>
            <EButton variant="outline" size="sm">顶部</EButton>
          </template>
          <div class="p-3 text-sm">顶部 Popover 内容</div>
        </EPopover>
        <EPopover side="bottom">
          <template #trigger>
            <EButton variant="outline" size="sm">底部</EButton>
          </template>
          <div class="p-3 text-sm">底部 Popover 内容</div>
        </EPopover>
        <EPopover side="left">
          <template #trigger>
            <EButton variant="outline" size="sm">左侧</EButton>
          </template>
          <div class="p-3 text-sm">左侧 Popover 内容</div>
        </EPopover>
        <EPopover side="right">
          <template #trigger>
            <EButton variant="outline" size="sm">右侧</EButton>
          </template>
          <div class="p-3 text-sm">右侧 Popover 内容</div>
        </EPopover>
      </div>
    </DemoBlock>
  </div>
</template>
