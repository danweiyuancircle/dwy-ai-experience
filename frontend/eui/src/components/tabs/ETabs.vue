<!--
  ETabs 标签页组件
  基于 reka-ui Tabs 封装，支持 top/bottom/left/right 四向布局
  可配置关闭按钮（closable）和新增按钮（addable），便于实现浏览器式多标签
-->
<script setup lang="ts">
import { computed } from 'vue'
import { X, Plus } from 'lucide-vue-next'
import {
  TabsRoot,
  TabsList,
  TabsTrigger,
  TabsContent,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ETabsProps, ETabsEmits } from './types'

const props = withDefaults(defineProps<ETabsProps>(), {
  items: () => [],
  closable: false,
  addable: false,
  tabPosition: 'top',
})

const emit = defineEmits<ETabsEmits>()

const isControlled = computed(() => props.modelValue !== undefined)

const initialDefault = computed(() => {
  return props.items && props.items.length > 0 ? props.items[0].key : undefined
})

/** 是否为纵向排列（左/右位置时） */
const isVertical = computed(() => props.tabPosition === 'left' || props.tabPosition === 'right')

/** 根容器布局 class，根据 tabPosition 决定 flex 方向 */
const rootLayoutClass = computed(() => {
  switch (props.tabPosition) {
    case 'bottom':
      return 'flex flex-col-reverse gap-2'
    case 'left':
      return 'flex flex-row gap-2'
    case 'right':
      return 'flex flex-row-reverse gap-2'
    default:
      return 'flex flex-col gap-2'
  }
})

/** 标签列表的 flex 排列 class */
const listLayoutClass = computed(() => {
  if (isVertical.value) {
    return 'bg-muted text-muted-foreground inline-flex w-fit flex-col items-stretch rounded-lg p-[3px]'
  }
  return 'bg-muted text-muted-foreground inline-flex h-9 w-fit items-center justify-center rounded-lg p-[3px]'
})

function onValueChange(value: string) {
  emit('update:modelValue', value)
  emit('change', value)
}

function onClose(event: MouseEvent, key: string) {
  event.stopPropagation()
  emit('close', key)
}

function onAdd() {
  emit('add')
}
</script>

<template>
  <TabsRoot
    data-slot="tabs"
    :model-value="isControlled ? props.modelValue : undefined"
    :default-value="!isControlled ? initialDefault : undefined"
    :class="cn(rootLayoutClass, props.class)"
    :orientation="isVertical ? 'vertical' : 'horizontal'"
    @update:model-value="onValueChange"
  >
    <div
      v-if="!isVertical"
      data-slot="tabs-list-wrap"
      class="w-full min-w-0 overflow-x-auto overscroll-x-contain"
    >
    <TabsList
      data-slot="tabs-list"
      :class="cn(listLayoutClass, 'w-max')"
    >
      <TabsTrigger
        v-for="item in items"
        :key="item.key"
        data-slot="tabs-trigger"
        :value="item.key"
        :disabled="item.disabled"
        :class="cn(
          'data-[state=active]:bg-background dark:data-[state=active]:text-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:outline-ring dark:data-[state=active]:border-input dark:data-[state=active]:bg-input/30 text-foreground dark:text-muted-foreground inline-flex h-[calc(100%-1px)] flex-1 items-center justify-center gap-1.5 rounded-md border border-transparent px-2 py-1 text-sm font-medium whitespace-nowrap transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:shadow-sm [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        )"
      >
        {{ item.label }}
        <button
          v-if="closable && !item.disabled"
          type="button"
          tabindex="-1"
          class="ml-1 inline-flex items-center justify-center rounded-sm opacity-60 hover:opacity-100 transition-opacity pointer-events-auto"
          @click="onClose($event, item.key)"
          @pointerdown.stop
        >
          <X class="size-3" />
        </button>
      </TabsTrigger>

      <!-- Add button -->
      <button
        v-if="addable"
        type="button"
        data-slot="tabs-add"
        :class="cn(
          'inline-flex items-center justify-center rounded-md px-2 py-1 text-sm text-muted-foreground hover:text-foreground hover:bg-background/60 transition-colors',
        )"
        @click="onAdd"
      >
        <Plus class="size-4" />
      </button>

      <slot name="extra" />
    </TabsList>
    </div>
    <TabsList
      v-else
      data-slot="tabs-list"
      :class="cn(listLayoutClass)"
    >
      <TabsTrigger
        v-for="item in items"
        :key="item.key"
        data-slot="tabs-trigger"
        :value="item.key"
        :disabled="item.disabled"
        :class="cn(
          'data-[state=active]:bg-background dark:data-[state=active]:text-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:outline-ring dark:data-[state=active]:border-input dark:data-[state=active]:bg-input/30 text-foreground dark:text-muted-foreground inline-flex h-[calc(100%-1px)] flex-1 items-center justify-center gap-1.5 rounded-md border border-transparent px-2 py-1 text-sm font-medium whitespace-nowrap transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:shadow-sm [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        )"
      >
        {{ item.label }}
        <button
          v-if="closable && !item.disabled"
          type="button"
          tabindex="-1"
          class="ml-1 inline-flex items-center justify-center rounded-sm opacity-60 hover:opacity-100 transition-opacity pointer-events-auto"
          @click="onClose($event, item.key)"
          @pointerdown.stop
        >
          <X class="size-3" />
        </button>
      </TabsTrigger>
      <button
        v-if="addable"
        type="button"
        data-slot="tabs-add"
        :class="cn(
          'inline-flex items-center justify-center rounded-md px-2 py-1 text-sm text-muted-foreground hover:text-foreground hover:bg-background/60 transition-colors',
        )"
        @click="onAdd"
      >
        <Plus class="size-4" />
      </button>
      <slot name="extra" />
    </TabsList>

    <TabsContent
      v-for="item in items"
      :key="item.key"
      data-slot="tabs-content"
      :value="item.key"
      :class="cn('flex-1 outline-none')"
    >
      <slot :name="`tab-${item.key}`" />
    </TabsContent>
  </TabsRoot>
</template>
