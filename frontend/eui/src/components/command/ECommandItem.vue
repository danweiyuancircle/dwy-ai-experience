<!--
  ECommandItem 命令面板条目组件
  挂载时向根 Command 注册自身文本内容用于搜索；选中时自动清空搜索词
-->
<script setup lang="ts">
import type { ListboxItemEmits, ListboxItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit, useCurrentElement } from '@vueuse/core'
import { ListboxItem, useForwardPropsEmits, useId } from 'reka-ui'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { cn } from '@/utils/cn'
import { useCommand, useCommandGroup } from './context'

const props = defineProps<ListboxItemProps & { class?: HTMLAttributes['class'] }>()
const emits = defineEmits<ListboxItemEmits>()
const delegatedProps = reactiveOmit(props, 'class')
const forwarded = useForwardPropsEmits(delegatedProps, emits)
const id = useId()
const { filterState, allItems, allGroups } = useCommand()
const groupContext = useCommandGroup()

// 无搜索词时全部可见；有搜索词时仅命中的条目可见
const isRender = computed(() => {
  if (!filterState.search) return true
  const filteredCurrentItem = filterState.filtered.items.get(id)
  if (filteredCurrentItem === undefined) return true
  return filteredCurrentItem > 0
})

const itemRef = ref()
const currentElement = useCurrentElement(itemRef)

// 挂载时读取 DOM 文本内容作为搜索语料，并登记到所属 group
onMounted(() => {
  if (!(currentElement.value instanceof HTMLElement)) return
  allItems.value.set(id, currentElement.value.textContent ?? (props.value?.toString() ?? ''))
  const groupId = groupContext?.id
  if (groupId) {
    if (!allGroups.value.has(groupId)) {
      allGroups.value.set(groupId, new Set([id]))
    } else {
      allGroups.value.get(groupId)?.add(id)
    }
  }
})

// 卸载时清理注册信息
onUnmounted(() => {
  allItems.value.delete(id)
})
</script>

<template>
  <ListboxItem
    v-if="isRender"
    v-bind="forwarded"
    :id="id"
    ref="itemRef"
    data-slot="command-item"
    :class="cn(
      'data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground',
      '[&_svg:not([class*=\'text-\'])]:text-muted-foreground',
      'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class,
    )"
    @select="() => { filterState.search = '' }"
  >
    <slot />
  </ListboxItem>
</template>
