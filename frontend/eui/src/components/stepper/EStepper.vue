<script setup lang="ts">
import {
  StepperDescription,
  StepperIndicator,
  StepperItem,
  StepperRoot,
  StepperSeparator,
  StepperTitle,
  StepperTrigger,
} from 'reka-ui'
import { Check } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EStepperProps, EStepperEmits } from './types'

const props = withDefaults(defineProps<EStepperProps>(), {
  items: () => [],
  direction: 'horizontal',
  modelValue: 1,
})

const emit = defineEmits<EStepperEmits>()

function onUpdate(val: number | undefined) {
  if (val !== undefined) emit('update:modelValue', val)
}
</script>

<template>
  <StepperRoot
    :model-value="modelValue"
    :orientation="direction"
    :class="cn(
      'flex gap-2',
      direction === 'vertical' ? 'flex-col' : 'flex-row items-start',
      props.class,
    )"
    @update:model-value="onUpdate"
  >
    <StepperItem
      v-for="(item, index) in items"
      :key="index"
      v-slot="{ state }"
      :step="index + 1"
      :class="cn(
        'flex items-center gap-2 group data-[disabled]:pointer-events-none',
        direction === 'vertical' ? 'flex-row' : 'flex-col flex-1',
      )"
    >
      <StepperTrigger class="flex flex-col items-center gap-1 rounded-md p-1 text-center">
        <StepperIndicator
          :class="cn(
            'inline-flex size-8 items-center justify-center rounded-full text-muted-foreground/50',
            'group-data-[disabled]:text-muted-foreground group-data-[disabled]:opacity-50',
            'group-data-[state=active]:bg-primary group-data-[state=active]:text-primary-foreground',
            'group-data-[state=completed]:bg-accent group-data-[state=completed]:text-accent-foreground',
          )"
        >
          <Check v-if="state === 'completed'" class="size-4" />
          <span v-else>{{ index + 1 }}</span>
        </StepperIndicator>
        <div class="flex flex-col items-center">
          <StepperTitle class="text-sm font-semibold whitespace-nowrap">
            {{ item.title }}
          </StepperTitle>
          <StepperDescription v-if="item.description" class="text-xs text-muted-foreground">
            {{ item.description }}
          </StepperDescription>
        </div>
      </StepperTrigger>

      <StepperSeparator
        v-if="index < items.length - 1"
        :class="cn(
          'bg-muted group-data-[state=completed]:bg-accent',
          direction === 'vertical' ? 'h-8 w-px ml-4' : 'h-px flex-1 self-center',
        )"
      />
    </StepperItem>
  </StepperRoot>
</template>
