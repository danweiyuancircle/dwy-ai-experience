<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">AspectRatio 宽高比</h1>
    <p class="text-muted-foreground mb-6">保持内容固定宽高比的容器。</p>

    <DemoBlock
      title="AspectRatio 宽高比"
      description="保持内容固定宽高比的容器"
      code='<EAspectRatio :ratio="16/9">
  <img src="..." class="object-cover w-full h-full" />
</EAspectRatio>'
    >
      <div class="grid grid-cols-3 gap-4">
        <div>
          <p class="text-xs text-muted-foreground mb-1">16:9</p>
          <EAspectRatio :ratio="16/9">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              16:9
            </div>
          </EAspectRatio>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">4:3</p>
          <EAspectRatio :ratio="4/3">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              4:3
            </div>
          </EAspectRatio>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">1:1</p>
          <EAspectRatio :ratio="1">
            <div class="bg-muted rounded-md w-full h-full flex items-center justify-center text-sm text-muted-foreground">
              1:1
            </div>
          </EAspectRatio>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
