<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Spinner 加载指示器</h1>
    <p class="text-muted-foreground mb-6">旋转加载指示器，支持 sm / default / lg 三种尺寸。</p>

    <DemoBlock
      title="Spinner 加载指示器"
      description="旋转加载指示器，支持 sm / default / lg 三种尺寸"
      code='<ESpinner />
<ESpinner size="lg" />'
    >
      <div class="flex items-center gap-6">
        <div class="flex flex-col items-center gap-2">
          <ESpinner size="sm" />
          <span class="text-xs text-muted-foreground">sm</span>
        </div>
        <div class="flex flex-col items-center gap-2">
          <ESpinner />
          <span class="text-xs text-muted-foreground">default</span>
        </div>
        <div class="flex flex-col items-center gap-2">
          <ESpinner size="lg" />
          <span class="text-xs text-muted-foreground">lg</span>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
