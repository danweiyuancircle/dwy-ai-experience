<!--
  EContextMenu 右键菜单组件
  基于 reka-ui ContextMenu 原语封装，支持多级子菜单与危险操作样式
  默认插槽作为触发区域，右键点击时弹出菜单
-->
<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import {
  ContextMenuRoot,
  ContextMenuTrigger,
  ContextMenuPortal,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuSub,
  ContextMenuSubTrigger,
  ContextMenuSubContent,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EContextMenuProps, EContextMenuEmits, ContextMenuItem as ContextMenuItemType } from './types'

const props = withDefaults(defineProps<EContextMenuProps>(), {
  items: () => [],
})

const emit = defineEmits<EContextMenuEmits>()

/** 将子组件 select 事件上浮 */
function handleSelect(key: string) {
  emit('select', key)
}
</script>

<template>
  <ContextMenuRoot>
    <ContextMenuTrigger data-slot="context-menu-trigger" as-child>
      <slot />
    </ContextMenuTrigger>

    <ContextMenuPortal>
      <ContextMenuContent
        data-slot="context-menu-content"
        :class="cn(
          'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 max-h-(--reka-context-menu-content-available-height) min-w-[8rem] overflow-x-hidden overflow-y-auto rounded-md border p-1 shadow-md',
          props.class,
        )"
      >
        <template v-for="item in items" :key="item.key">
          <ContextMenuSeparator
            v-if="item.divided"
            data-slot="context-menu-separator"
            class="bg-border -mx-1 my-1 h-px"
          />

          <!-- Sub-menu item -->
          <ContextMenuSub v-if="item.children && item.children.length > 0">
            <ContextMenuSubTrigger
              data-slot="context-menu-sub-trigger"
              :disabled="item.disabled"
              :class="cn(
                'focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
              )"
            >
              <component :is="item.icon" v-if="item.icon" />
              {{ item.label }}
              <ChevronRight class="ml-auto size-4" />
            </ContextMenuSubTrigger>
            <ContextMenuPortal>
              <ContextMenuSubContent
                data-slot="context-menu-sub-content"
                :class="cn(
                  'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 z-50 min-w-[8rem] overflow-hidden rounded-md border p-1 shadow-lg',
                )"
              >
                <template v-for="child in item.children" :key="child.key">
                  <ContextMenuSeparator
                    v-if="child.divided"
                    data-slot="context-menu-separator"
                    class="bg-border -mx-1 my-1 h-px"
                  />
                  <ContextMenuItem
                    data-slot="context-menu-item"
                    :disabled="child.disabled"
                    :data-variant="child.variant ?? 'default'"
                    :class="cn(
                      'focus:bg-accent focus:text-accent-foreground data-[variant=destructive]:text-destructive data-[variant=destructive]:focus:bg-destructive/10 dark:data-[variant=destructive]:focus:bg-destructive/20 [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
                    )"
                    @select="handleSelect(child.key)"
                  >
                    <component :is="child.icon" v-if="child.icon" />
                    {{ child.label }}
                  </ContextMenuItem>
                </template>
              </ContextMenuSubContent>
            </ContextMenuPortal>
          </ContextMenuSub>

          <!-- Regular item -->
          <ContextMenuItem
            v-else
            data-slot="context-menu-item"
            :disabled="item.disabled"
            :data-variant="item.variant ?? 'default'"
            :class="cn(
              'focus:bg-accent focus:text-accent-foreground data-[variant=destructive]:text-destructive data-[variant=destructive]:focus:bg-destructive/10 dark:data-[variant=destructive]:focus:bg-destructive/20 [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
            )"
            @select="handleSelect(item.key)"
          >
            <component :is="item.icon" v-if="item.icon" />
            {{ item.label }}
          </ContextMenuItem>
        </template>
      </ContextMenuContent>
    </ContextMenuPortal>
  </ContextMenuRoot>
</template>
