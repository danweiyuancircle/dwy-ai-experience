<script setup lang="ts">
import { computed, watch } from 'vue'
import { X } from 'lucide-vue-next'
import {
  DrawerRoot,
  DrawerPortal,
  DrawerOverlay,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
  DrawerClose,
  DrawerTrigger,
} from 'vaul-vue'
import { cn } from '@/utils/cn'
import type { EDrawerProps, EDrawerEmits } from './types'

const props = withDefaults(defineProps<EDrawerProps>(), {
  direction: 'bottom',
  showClose: true,
})

const emit = defineEmits<EDrawerEmits>()

const isOpen = computed({
  get: () => props.open ?? false,
  set: (value: boolean) => emit('update:open', value),
})

watch(isOpen, (value) => {
  if (!value) {
    emit('close')
  }
})
</script>

<template>
  <DrawerRoot
    v-model:open="isOpen"
    data-slot="drawer"
    :direction="direction"
    :should-scale-background="true"
  >
    <DrawerTrigger
      v-if="$slots.trigger"
      data-slot="drawer-trigger"
      as-child
    >
      <slot name="trigger" />
    </DrawerTrigger>

    <DrawerPortal>
      <DrawerOverlay
        data-slot="drawer-overlay"
        :class="cn(
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80',
        )"
      />

      <DrawerContent
        data-slot="drawer-content"
        :class="cn(
          'group/drawer-content bg-background fixed z-50 flex h-auto flex-col',
          'data-[vaul-drawer-direction=top]:inset-x-0 data-[vaul-drawer-direction=top]:top-0 data-[vaul-drawer-direction=top]:mb-24 data-[vaul-drawer-direction=top]:max-h-[80vh] data-[vaul-drawer-direction=top]:rounded-b-lg',
          'data-[vaul-drawer-direction=bottom]:inset-x-0 data-[vaul-drawer-direction=bottom]:bottom-0 data-[vaul-drawer-direction=bottom]:mt-24 data-[vaul-drawer-direction=bottom]:max-h-[80vh] data-[vaul-drawer-direction=bottom]:rounded-t-lg',
          'data-[vaul-drawer-direction=right]:inset-y-0 data-[vaul-drawer-direction=right]:right-0 data-[vaul-drawer-direction=right]:w-3/4 data-[vaul-drawer-direction=right]:sm:max-w-sm',
          'data-[vaul-drawer-direction=left]:inset-y-0 data-[vaul-drawer-direction=left]:left-0 data-[vaul-drawer-direction=left]:w-3/4 data-[vaul-drawer-direction=left]:sm:max-w-sm',
          props.class,
        )"
      >
        <!-- Drag handle for bottom drawer -->
        <div class="bg-muted mx-auto mt-4 hidden h-2 w-[100px] shrink-0 rounded-full group-data-[vaul-drawer-direction=bottom]/drawer-content:block" />

        <!-- Header -->
        <div
          v-if="title || description || $slots.header"
          data-slot="drawer-header"
          :class="cn('flex flex-col gap-1.5 p-4')"
        >
          <slot name="header">
            <DrawerTitle
              v-if="title"
              data-slot="drawer-title"
              :class="cn('text-foreground font-semibold')"
            >
              {{ title }}
            </DrawerTitle>
            <DrawerDescription
              v-if="description"
              data-slot="drawer-description"
              :class="cn('text-muted-foreground text-sm')"
            >
              {{ description }}
            </DrawerDescription>
          </slot>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-auto px-4">
          <slot />
        </div>

        <!-- Footer -->
        <div
          v-if="$slots.footer"
          data-slot="drawer-footer"
          :class="cn('mt-auto flex flex-col gap-2 p-4')"
        >
          <slot name="footer" />
        </div>

        <!-- Close button -->
        <DrawerClose
          v-if="showClose"
          data-slot="drawer-close"
          class="ring-offset-background focus:ring-ring absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-offset-2 focus:outline-hidden disabled:pointer-events-none"
        >
          <X class="size-4" />
          <span class="sr-only">Close</span>
        </DrawerClose>
      </DrawerContent>
    </DrawerPortal>
  </DrawerRoot>
</template>
