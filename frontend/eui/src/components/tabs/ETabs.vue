<script setup lang="ts">
import { computed } from 'vue'
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
})

const emit = defineEmits<ETabsEmits>()

const isControlled = computed(() => props.modelValue !== undefined)

const initialDefault = computed(() => {
  return props.items && props.items.length > 0 ? props.items[0].key : undefined
})

function onValueChange(value: string) {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<template>
  <TabsRoot
    data-slot="tabs"
    :model-value="isControlled ? props.modelValue : undefined"
    :default-value="!isControlled ? initialDefault : undefined"
    :class="cn('flex flex-col gap-2', props.class)"
    @update:model-value="onValueChange"
  >
    <TabsList
      data-slot="tabs-list"
      :class="cn(
        'bg-muted text-muted-foreground inline-flex h-9 w-fit items-center justify-center rounded-lg p-[3px]',
      )"
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
      </TabsTrigger>
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
