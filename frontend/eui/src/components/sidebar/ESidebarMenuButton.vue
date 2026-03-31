<script setup lang="ts">
import type { Component } from 'vue'
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { SidebarMenuButtonVariants } from './utils'
import { reactiveOmit } from '@vueuse/core'
import { Primitive } from 'reka-ui'
import { TooltipContent, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import { sidebarMenuButtonVariants, useSidebar } from './utils'

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<PrimitiveProps & {
  variant?: SidebarMenuButtonVariants['variant']
  size?: SidebarMenuButtonVariants['size']
  isActive?: boolean
  tooltip?: string | Component
  class?: HTMLAttributes['class']
}>(), {
  as: 'button',
  variant: 'default',
  size: 'default',
})

const { isMobile, state } = useSidebar()
const delegatedProps = reactiveOmit(props, 'tooltip', 'class', 'variant', 'size', 'isActive', 'as', 'asChild')
</script>

<template>
  <Primitive
    v-if="!tooltip"
    data-slot="sidebar-menu-button"
    data-sidebar="menu-button"
    :data-size="size"
    :data-active="isActive"
    :class="cn(sidebarMenuButtonVariants({ variant, size }), props.class)"
    :as="as"
    :as-child="asChild"
    v-bind="{ ...delegatedProps, ...$attrs }"
  >
    <slot />
  </Primitive>

  <TooltipProvider v-else :delay-duration="0">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <Primitive
          data-slot="sidebar-menu-button"
          data-sidebar="menu-button"
          :data-size="size"
          :data-active="isActive"
          :class="cn(sidebarMenuButtonVariants({ variant, size }), props.class)"
          :as="as"
          :as-child="asChild"
          v-bind="{ ...delegatedProps, ...$attrs }"
        >
          <slot />
        </Primitive>
      </TooltipTrigger>
      <TooltipContent
        side="right"
        align="center"
        :hidden="state !== 'collapsed' || isMobile"
      >
        <template v-if="typeof tooltip === 'string'">{{ tooltip }}</template>
        <component :is="tooltip" v-else />
      </TooltipContent>
    </TooltipRoot>
  </TooltipProvider>
</template>
