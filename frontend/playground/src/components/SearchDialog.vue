<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { search, type SearchItem } from '../data/search-index'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const router = useRouter()
const query = ref('')
const results = ref<SearchItem[]>([])
const inputRef = ref<HTMLInputElement>()

watch(query, (val) => {
  results.value = search(val)
})

watch(() => props.open, async (val) => {
  if (val) {
    query.value = ''
    results.value = []
    await nextTick()
    inputRef.value?.focus()
  }
})

function handleSelect(item: SearchItem) {
  router.push(item.path)
  emit('update:open', false)
}

function handleOpenChange(val: boolean) {
  emit('update:open', val)
}

function groupedResults() {
  const groups: Record<string, SearchItem[]> = {}
  for (const item of results.value) {
    if (!groups[item.module]) groups[item.module] = []
    groups[item.module].push(item)
  }
  return groups
}
</script>

<template>
  <EDialog
    :open="open"
    title="搜索"
    :show-close="false"
    max-width="560px"
    class="p-0 gap-0 [&>[data-slot=dialog-header]]:hidden"
    @update:open="handleOpenChange"
  >
    <!-- Search input -->
    <div class="flex items-center border-b px-3">
      <svg class="size-4 shrink-0 opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input
        ref="inputRef"
        v-model="query"
        placeholder="搜索页面..."
        class="flex h-12 w-full bg-transparent py-3 pl-3 text-sm outline-none placeholder:text-muted-foreground"
      />
      <button @click="emit('update:open', false)" class="text-xs text-muted-foreground border rounded px-1.5 py-0.5 hover:bg-accent transition-colors">ESC</button>
    </div>

    <!-- Results (fixed height) -->
    <div class="h-[360px] overflow-y-auto p-2">
      <template v-if="results.length > 0">
        <template v-for="(items, module) in groupedResults()" :key="module">
          <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">{{ module }}</div>
          <button
            v-for="item in items"
            :key="item.path"
            class="flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm hover:bg-accent transition-colors text-left"
            @click="handleSelect(item)"
          >
            <span class="flex-1">{{ item.title }}</span>
            <span class="text-xs text-muted-foreground">{{ item.module }}</span>
          </button>
        </template>
      </template>
      <div v-else-if="query.trim()" class="flex items-center justify-center h-full text-sm text-muted-foreground">
        无匹配结果
      </div>
      <div v-else class="flex items-center justify-center h-full text-sm text-muted-foreground">
        输入关键词搜索所有模块...
      </div>
    </div>
  </EDialog>
</template>
