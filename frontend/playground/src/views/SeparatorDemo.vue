<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Separator 分隔线</h1>
    <p class="text-muted-foreground mb-6">水平或垂直方向的分隔线。</p>

    <DemoBlock
      title="Separator 分隔线"
      description="水平或垂直方向的分隔线"
      code='<ESeparator />
<ESeparator orientation="vertical" />'
    >
      <div class="space-y-4">
        <!-- 水平 -->
        <div>
          <p class="text-sm mb-2">水平分隔线</p>
          <div>文字内容上方</div>
          <ESeparator class="my-3" />
          <div>文字内容下方</div>
        </div>
        <!-- 垂直 -->
        <div>
          <p class="text-sm mb-2">垂直分隔线</p>
          <div class="flex items-center gap-4 h-8">
            <span>左侧内容</span>
            <ESeparator orientation="vertical" />
            <span>右侧内容</span>
            <ESeparator orientation="vertical" />
            <span>更多内容</span>
          </div>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
