<script setup lang="ts">
export interface SlotItem {
  name: string
  props?: string
  description: string
}

defineProps<{ data: SlotItem[] }>()
</script>

<template>
  <div>
    <h2 class="text-lg font-semibold mb-3">Slots</h2>
    <div class="border rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b bg-muted/50">
            <th class="text-left font-medium px-4 py-2.5 w-[180px]">插槽名</th>
            <th class="text-left font-medium px-4 py-2.5 w-[240px]">插槽参数</th>
            <th class="text-left font-medium px-4 py-2.5">说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in data" :key="item.name" class="border-b last:border-b-0">
            <td class="px-4 py-2.5"><code class="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{{ item.name }}</code></td>
            <td class="px-4 py-2.5 text-muted-foreground"><code v-if="item.props" class="text-xs font-mono">{{ item.props }}</code><span v-else class="text-muted-foreground/50">—</span></td>
            <td class="px-4 py-2.5">{{ item.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
