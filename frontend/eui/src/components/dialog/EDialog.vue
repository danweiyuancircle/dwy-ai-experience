<script setup lang="ts">
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
  DialogTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EDialogProps, EDialogEmits } from './types'

const props = withDefaults(defineProps<EDialogProps>(), {
  showClose: true,
})

const emit = defineEmits<EDialogEmits>()

// Use a local ref synced with the prop — reka-ui DialogRoot works best with v-model:open on a ref
const localOpen = ref(props.open ?? false)

watch(() => props.open, (val) => {
  localOpen.value = val ?? false
})

watch(localOpen, (val) => {
  emit('update:open', val)
  if (val) emit('open')
  else emit('close')
})
</script>

<template>
  <DialogRoot
    v-model:open="localOpen"
    data-slot="dialog"
  >
    <DialogTrigger
      v-if="$slots.trigger"
      data-slot="dialog-trigger"
      as-child
    >
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay
        data-slot="dialog-overlay"
        :class="cn(
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80',
        )"
      />

      <DialogContent
        data-slot="dialog-content"
        :class="cn(
          'bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg duration-200 sm:max-w-lg',
          props.class,
        )"
        :style="maxWidth ? { maxWidth } : undefined"
      >
        <div
          v-if="title || description || $slots.header"
          data-slot="dialog-header"
          :class="cn('flex flex-col gap-2 text-center sm:text-left')"
        >
          <slot name="header">
            <DialogTitle
              v-if="title"
              data-slot="dialog-title"
              :class="cn('text-lg leading-none font-semibold')"
            >
              {{ title }}
            </DialogTitle>
            <DialogDescription
              v-if="description"
              data-slot="dialog-description"
              :class="cn('text-muted-foreground text-sm')"
            >
              {{ description }}
            </DialogDescription>
          </slot>
        </div>

        <slot />

        <div
          v-if="$slots.footer"
          data-slot="dialog-footer"
          :class="cn('flex flex-col-reverse gap-2 sm:flex-row sm:justify-end')"
        >
          <slot name="footer" />
        </div>

        <DialogClose
          v-if="showClose"
          data-slot="dialog-close"
          class="ring-offset-background focus:ring-ring data-[state=open]:bg-accent data-[state=open]:text-muted-foreground absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-offset-2 focus:outline-hidden disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4"
        >
          <X />
          <span class="sr-only">Close</span>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
