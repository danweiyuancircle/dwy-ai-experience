<script setup lang="ts">
export interface PropItem {
  name: string
  type: string
  default?: string
  description: string
}

defineProps<{ data: PropItem[] }>()
</script>

<template>
  <div>
    <h2 class="text-lg font-semibold mb-3">Props</h2>
    <div class="border rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b bg-muted/50">
            <th class="text-left font-medium px-4 py-2.5 w-[160px]">属性</th>
            <th class="text-left font-medium px-4 py-2.5 w-[200px]">类型</th>
            <th class="text-left font-medium px-4 py-2.5 w-[100px]">默认值</th>
            <th class="text-left font-medium px-4 py-2.5">说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in data" :key="item.name" class="border-b last:border-b-0">
            <td class="px-4 py-2.5"><code class="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{{ item.name }}</code></td>
            <td class="px-4 py-2.5 text-muted-foreground"><code class="text-xs font-mono">{{ item.type }}</code></td>
            <td class="px-4 py-2.5 text-muted-foreground"><code v-if="item.default" class="text-xs font-mono">{{ item.default }}</code><span v-else class="text-muted-foreground/50">—</span></td>
            <td class="px-4 py-2.5">{{ item.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
