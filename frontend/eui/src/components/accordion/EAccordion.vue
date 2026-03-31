<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import {
  AccordionContent,
  AccordionHeader,
  AccordionItem,
  AccordionRoot,
  AccordionTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EAccordionProps, EAccordionEmits } from './types'

const props = withDefaults(defineProps<EAccordionProps>(), {
  multiple: false,
  collapsible: true,
})

const emit = defineEmits<EAccordionEmits>()

function onUpdate(value: string | string[] | undefined) {
  emit('update:modelValue', value)
}
</script>

<template>
  <AccordionRoot
    data-slot="accordion"
    :type="multiple ? 'multiple' : 'single'"
    :model-value="modelValue as any"
    :collapsible="!multiple ? collapsible : undefined"
    :class="cn(props.class)"
    @update:model-value="onUpdate"
  >
    <template v-if="items && items.length">
      <AccordionItem
        v-for="item in items"
        :key="item.key"
        data-slot="accordion-item"
        :value="item.key"
        :disabled="item.disabled"
        :class="cn('border-b last:border-b-0')"
      >
        <AccordionHeader class="flex">
          <AccordionTrigger
            data-slot="accordion-trigger"
            :class="cn(
              'focus-visible:border-ring focus-visible:ring-ring/50 flex flex-1 items-start justify-between gap-4 rounded-md py-4 text-left text-sm font-medium transition-all outline-none hover:underline focus-visible:ring-[3px] disabled:pointer-events-none disabled:opacity-50 [&[data-state=open]>svg]:rotate-180',
            )"
          >
            {{ item.title }}
            <ChevronDown
              class="text-muted-foreground pointer-events-none size-4 shrink-0 translate-y-0.5 transition-transform duration-200"
            />
          </AccordionTrigger>
        </AccordionHeader>
        <AccordionContent
          data-slot="accordion-content"
          class="data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down overflow-hidden text-sm"
        >
          <div class="pt-0 pb-4">
            <slot :name="item.key" :item="item" />
          </div>
        </AccordionContent>
      </AccordionItem>
    </template>

    <slot v-else />
  </AccordionRoot>
</template>
