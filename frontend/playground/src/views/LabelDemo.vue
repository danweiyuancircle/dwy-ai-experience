<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Label 标签</h1>
    <p class="text-muted-foreground mb-6">用于关联表单控件的标签元素。</p>

    <DemoBlock
      title="Label 标签"
      description="用于关联表单控件的标签元素"
      code='<ELabel for="inputId">用户名</ELabel>
<EInput id="inputId" placeholder="请输入" />'
    >
      <div class="space-y-4 max-w-sm">
        <div class="space-y-1.5">
          <ELabel for="demo-input">用户名</ELabel>
          <EInput id="demo-input" placeholder="请输入用户名" />
        </div>
        <div class="space-y-1.5">
          <ELabel for="demo-email">邮箱地址</ELabel>
          <EInput id="demo-email" placeholder="请输入邮箱" />
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
