<script setup lang="ts">
import { ref } from 'vue'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'
import {
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { buttonVariants } from '@/components/button/types'
import type { EDropdownProps, EDropdownEmits, DropdownMenuItem as DropdownMenuItemType } from './types'

const props = withDefaults(defineProps<EDropdownProps>(), {
  items: () => [],
  side: 'bottom',
  align: 'start',
  sideOffset: 4,
  trigger: 'click',
  splitButton: false,
  buttonVariant: 'outline',
})

const emit = defineEmits<EDropdownEmits>()

const isOpen = ref(false)
let hoverCloseTimer: ReturnType<typeof setTimeout> | undefined

function handleSelect(key: string) {
  emit('select', key)
}

function handleButtonClick() {
  emit('click')
}

function handleMouseEnter() {
  if (props.trigger !== 'hover') return
  clearTimeout(hoverCloseTimer)
  isOpen.value = true
}

function handleMouseLeave() {
  if (props.trigger !== 'hover') return
  hoverCloseTimer = setTimeout(() => {
    isOpen.value = false
  }, 200)
}

function handleOpenChange(open: boolean) {
  isOpen.value = open
}

const menuContentClass = cn(
  'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 max-h-(--reka-dropdown-menu-content-available-height) min-w-[8rem] origin-(--reka-dropdown-menu-content-transform-origin) overflow-x-hidden overflow-y-auto rounded-md border p-1 shadow-md',
)

const menuItemClass = cn(
  "focus:bg-accent focus:text-accent-foreground data-[variant=destructive]:text-destructive data-[variant=destructive]:focus:bg-destructive/10 dark:data-[variant=destructive]:focus:bg-destructive/20 data-[variant=destructive]:focus:text-destructive data-[variant=destructive]:*:[svg]:!text-destructive [&_svg:not([class*='text-'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
)

const subTriggerClass = cn(
  "focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 data-[variant=destructive]:*:[svg]:!text-destructive [&_svg:not([class*='text-'])]:text-muted-foreground",
)

const subContentClass = cn(
  'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 min-w-[8rem] origin-(--reka-dropdown-menu-content-transform-origin) overflow-hidden rounded-md border p-1 shadow-lg',
)
</script>

<template>
  <DropdownMenuRoot
    :open="isOpen"
    @update:open="handleOpenChange"
  >
    <!-- Split button mode -->
    <div
      v-if="splitButton"
      data-slot="dropdown-split-button"
      :class="cn('inline-flex items-center rounded-md', props.class)"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <button
        data-slot="dropdown-split-primary"
        :class="cn(
          buttonVariants({ variant: buttonVariant as any, size: 'default' }),
          'rounded-r-none border-r-0',
        )"
        @click="handleButtonClick"
      >
        {{ buttonText }}
      </button>
      <DropdownMenuTrigger data-slot="dropdown-menu-trigger" as-child>
        <button
          data-slot="dropdown-split-arrow"
          :class="cn(
            buttonVariants({ variant: buttonVariant as any, size: 'icon' }),
            'rounded-l-none',
          )"
        >
          <ChevronDown class="size-4" />
        </button>
      </DropdownMenuTrigger>
    </div>

    <!-- Regular trigger mode -->
    <div
      v-else
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <DropdownMenuTrigger data-slot="dropdown-menu-trigger" as-child>
        <slot />
      </DropdownMenuTrigger>
    </div>

    <DropdownMenuPortal>
      <DropdownMenuContent
        data-slot="dropdown-menu-content"
        :side="side"
        :align="align"
        :side-offset="sideOffset"
        :class="cn(menuContentClass, props.class)"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
      >
        <template v-for="item in items" :key="item.key">
          <DropdownMenuSeparator
            v-if="item.divided"
            data-slot="dropdown-menu-separator"
            class="bg-border -mx-1 my-1 h-px"
          />

          <!-- Sub-menu item -->
          <DropdownMenuSub v-if="item.children && item.children.length > 0">
            <DropdownMenuSubTrigger
              data-slot="dropdown-menu-sub-trigger"
              :disabled="item.disabled"
              :class="subTriggerClass"
            >
              <component :is="item.icon" v-if="item.icon" />
              {{ item.label }}
              <ChevronRight class="ml-auto size-4" />
            </DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              <DropdownMenuSubContent
                data-slot="dropdown-menu-sub-content"
                :class="subContentClass"
              >
                <template v-for="child in item.children" :key="child.key">
                  <DropdownMenuSeparator
                    v-if="child.divided"
                    data-slot="dropdown-menu-separator"
                    class="bg-border -mx-1 my-1 h-px"
                  />
                  <DropdownMenuItem
                    data-slot="dropdown-menu-item"
                    :disabled="child.disabled"
                    :data-variant="child.variant ?? 'default'"
                    :class="menuItemClass"
                    @select="handleSelect(child.key)"
                  >
                    <component :is="child.icon" v-if="child.icon" />
                    {{ child.label }}
                  </DropdownMenuItem>
                </template>
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>

          <!-- Regular item -->
          <DropdownMenuItem
            v-else
            data-slot="dropdown-menu-item"
            :disabled="item.disabled"
            :data-variant="item.variant ?? 'default'"
            :class="menuItemClass"
            @select="handleSelect(item.key)"
          >
            <component :is="item.icon" v-if="item.icon" />
            {{ item.label }}
          </DropdownMenuItem>
        </template>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>
