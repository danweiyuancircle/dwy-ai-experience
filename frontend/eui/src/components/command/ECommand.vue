<!--
  ECommand 命令面板根组件
  基于 reka-ui Listbox 原语封装，通过 Intl.Collator 做大小写/重音不敏感过滤
  通过 provide 向子组件分发搜索状态与全量条目/分组索引
-->
<script setup lang="ts">
import type { ListboxRootEmits, ListboxRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { ListboxRoot, useFilter, useForwardPropsEmits } from 'reka-ui'
import { reactive, ref, watch } from 'vue'
import { cn } from '@/utils/cn'
import { provideCommandContext } from './context'

const props = withDefaults(defineProps<ListboxRootProps & { class?: HTMLAttributes['class'] }>(), {
  modelValue: '',
})

const emits = defineEmits<ListboxRootEmits>()
const delegatedProps = reactiveOmit(props, 'class')
const forwarded = useForwardPropsEmits(delegatedProps, emits)

const allItems = ref<Map<string, string>>(new Map())
const allGroups = ref<Map<string, Set<string>>>(new Map())

// sensitivity: 'base' 表示忽略大小写与重音，提升搜索命中率
const { contains } = useFilter({ sensitivity: 'base' })
const filterState = reactive({
  search: '',
  filtered: {
    count: 0,
    items: new Map() as Map<string, number>,
    groups: new Set() as Set<string>,
  },
})

/**
 * 根据搜索关键词过滤全量 item，并根据 item 的命中情况推导可见 group
 */
function filterItems() {
  if (!filterState.search) {
    filterState.filtered.count = allItems.value.size
    return
  }
  filterState.filtered.groups = new Set()
  let itemCount = 0
  for (const [id, value] of allItems.value) {
    const score = contains(value, filterState.search)
    filterState.filtered.items.set(id, score ? 1 : 0)
    if (score) itemCount++
  }
  for (const [groupId, group] of allGroups.value) {
    for (const itemId of group) {
      if (filterState.filtered.items.get(itemId)! > 0) {
        filterState.filtered.groups.add(groupId)
        break
      }
    }
  }
  filterState.filtered.count = itemCount
}

// 搜索关键词变化时重新过滤
watch(() => filterState.search, filterItems)

provideCommandContext({ allItems, allGroups, filterState })
</script>

<template>
  <ListboxRoot
    data-slot="command"
    v-bind="forwarded"
    :class="cn('bg-popover text-popover-foreground flex h-full w-full flex-col overflow-hidden rounded-md', props.class)"
  >
    <slot />
  </ListboxRoot>
</template>
