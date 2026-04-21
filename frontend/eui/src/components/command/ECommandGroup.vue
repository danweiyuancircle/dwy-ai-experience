<!--
  ECommandGroup 命令面板分组组件
  用 heading 展示分组标题；挂载时向根 Command 注册自身 id
  搜索时若组内无命中条目则整组隐藏
-->
<script setup lang="ts">
import type { ListboxGroupProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { ListboxGroup, ListboxGroupLabel, useId } from 'reka-ui'
import { computed, onMounted, onUnmounted } from 'vue'
import { cn } from '@/utils/cn'
import { provideCommandGroupContext, useCommand } from './context'

const props = defineProps<ListboxGroupProps & {
  class?: HTMLAttributes['class']
  /** 分组标题 */
  heading?: string
}>()
const delegatedProps = reactiveOmit(props, 'class')
const { allGroups, filterState } = useCommand()
const id = useId()
// 无搜索词时始终可见；搜索时仅展示命中的分组
const isRender = computed(() => (!filterState.search ? true : filterState.filtered.groups.has(id)))

provideCommandGroupContext({ id })

// 向根 Command 注册本分组
onMounted(() => {
  if (!allGroups.value.has(id)) allGroups.value.set(id, new Set())
})
// 卸载时清理注册信息，避免内存泄漏
onUnmounted(() => {
  allGroups.value.delete(id)
})
</script>

<template>
  <ListboxGroup
    v-bind="delegatedProps"
    :id="id"
    data-slot="command-group"
    :class="cn('text-foreground overflow-hidden p-1', props.class)"
    :hidden="isRender ? undefined : true"
  >
    <ListboxGroupLabel
      v-if="heading"
      data-slot="command-group-heading"
      class="px-2 py-1.5 text-xs font-medium text-muted-foreground"
    >
      {{ heading }}
    </ListboxGroupLabel>
    <slot />
  </ListboxGroup>
</template>
