<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Kbd 键盘按键</h1>
    <p class="text-muted-foreground mb-6">用于展示快捷键的键盘样式组件。</p>

    <DemoBlock
      title="Kbd 键盘按键"
      description="用于展示快捷键的键盘样式组件"
      code='<EKbd>Ctrl</EKbd> + <EKbd>C</EKbd>'
    >
      <div class="space-y-4">
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Ctrl</EKbd>
          <span>+</span>
          <EKbd>C</EKbd>
          <span class="text-muted-foreground ml-2">复制</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Ctrl</EKbd>
          <span>+</span>
          <EKbd>V</EKbd>
          <span class="text-muted-foreground ml-2">粘贴</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>⌘</EKbd>
          <span>+</span>
          <EKbd>K</EKbd>
          <span class="text-muted-foreground ml-2">打开命令面板</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <EKbd>Escape</EKbd>
          <span class="text-muted-foreground ml-2">关闭对话框</span>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
