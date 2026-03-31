<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Empty 空状态</h1>
    <p class="text-muted-foreground mb-6">数据为空时的占位展示。</p>

    <DemoBlock
      title="Empty 空状态"
      description="数据为空时的占位展示"
      code='<EEmpty title="暂无数据" description="添加一些数据后这里会显示内容" />'
    >
      <div class="space-y-6">
        <EEmpty />
        <ESeparator />
        <EEmpty title="暂无数据" description="点击上方按钮添加第一条记录" />
      </div>
    </DemoBlock>
  </div>
</template>
