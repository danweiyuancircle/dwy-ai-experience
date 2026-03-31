<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
  description?: string
  code?: string
}>()

const showCode = ref(false)
</script>

<template>
  <div class="mb-8 border rounded-lg overflow-hidden">
    <div class="p-4 border-b bg-muted/30">
      <h3 class="font-semibold text-base">{{ title }}</h3>
      <p v-if="description" class="text-sm text-muted-foreground mt-1">{{ description }}</p>
    </div>
    <div class="p-6">
      <slot />
    </div>
    <div v-if="code" class="border-t">
      <button
        class="w-full px-4 py-2 text-xs text-muted-foreground hover:text-foreground text-center hover:bg-muted/50 transition-colors"
        @click="showCode = !showCode"
      >
        {{ showCode ? '隐藏代码' : '查看代码' }}
      </button>
      <pre v-if="showCode" class="p-4 bg-muted/50 text-sm overflow-x-auto border-t"><code>{{ code }}</code></pre>
    </div>
  </div>
</template>
