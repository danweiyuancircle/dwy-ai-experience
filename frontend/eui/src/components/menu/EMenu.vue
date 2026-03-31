<script setup lang="ts">
import { ref, getCurrentInstance } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import {
  CollapsibleRoot,
  CollapsibleTrigger,
  CollapsibleContent,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenuProps, EMenuEmits } from './types'
import type { MenuItem } from '@/types'

const props = withDefaults(defineProps<EMenuProps>(), {
  items: () => [],
  collapsed: false,
  router: false,
  uniqueOpened: false,
  defaultOpeneds: () => [],
})

const emit = defineEmits<EMenuEmits>()

const expandedKeys = ref<Set<string>>(new Set(props.defaultOpeneds))

/**
 * Resolve the vue-router instance from the app's global properties.
 * vue-router registers $router on globalProperties via app.use(router).
 * This avoids a hard import dependency on the vue-router package.
 */
const routerInstance = props.router
  ? (getCurrentInstance()?.appContext.config.globalProperties.$router as
      | { push: (to: string) => void }
      | undefined)
  : undefined

function isActive(key: string): boolean {
  return props.modelValue === key
}

function isExpanded(key: string): boolean {
  return expandedKeys.value.has(key)
}

function toggleExpand(key: string) {
  const next = new Set(expandedKeys.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    if (props.uniqueOpened) {
      // Close all other expanded sub-menus
      next.clear()
    }
    next.add(key)
  }
  expandedKeys.value = next
}

function handleSelect(item: MenuItem) {
  emit('update:modelValue', item.key)
  emit('select', item.key)

  if (props.router) {
    routerInstance?.push(item.path || item.key)
  }
}

function hasChildren(item: MenuItem): boolean {
  return !!item.children && item.children.length > 0
}
</script>

<template>
  <nav
    data-slot="menu"
    :class="cn(
      'flex flex-col gap-1',
      collapsed ? 'w-14' : 'w-56',
      'transition-[width] duration-200',
      props.class,
    )"
  >
    <template v-for="item in items" :key="item.key">
      <!-- Item with children (collapsible) -->
      <CollapsibleRoot
        v-if="hasChildren(item) && !collapsed"
        :open="isExpanded(item.key)"
        @update:open="toggleExpand(item.key)"
      >
        <CollapsibleTrigger
          :disabled="item.disabled"
          :class="cn(
            'flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
            'hover:bg-accent hover:text-accent-foreground',
            item.disabled && 'pointer-events-none opacity-50',
          )"
        >
          <component
            :is="item.icon"
            v-if="item.icon"
            class="size-4 shrink-0"
          />
          <span class="flex-1 text-left">{{ item.label }}</span>
          <ChevronDown
            :class="cn(
              'size-4 shrink-0 transition-transform duration-200',
              isExpanded(item.key) && 'rotate-180',
            )"
          />
        </CollapsibleTrigger>

        <CollapsibleContent
          class="overflow-hidden data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:slide-out-to-top-1 data-[state=open]:slide-in-from-top-1"
        >
          <div class="ml-4 mt-1 flex flex-col gap-1 border-l pl-2">
            <button
              v-for="child in item.children"
              :key="child.key"
              :disabled="child.disabled"
              :class="cn(
                'flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors',
                'hover:bg-accent hover:text-accent-foreground',
                isActive(child.key) && 'bg-primary/10 text-primary font-medium',
                child.disabled && 'pointer-events-none opacity-50',
              )"
              @click="handleSelect(child)"
            >
              <component
                :is="child.icon"
                v-if="child.icon"
                class="size-4 shrink-0"
              />
              <span>{{ child.label }}</span>
            </button>
          </div>
        </CollapsibleContent>
      </CollapsibleRoot>

      <!-- Simple item (no children) or collapsed mode -->
      <button
        v-else
        :disabled="item.disabled"
        :class="cn(
          'flex items-center rounded-md text-sm font-medium transition-colors',
          'hover:bg-accent hover:text-accent-foreground',
          isActive(item.key) && 'bg-primary/10 text-primary',
          item.disabled && 'pointer-events-none opacity-50',
          collapsed ? 'justify-center px-0 py-2' : 'gap-2 px-3 py-2',
        )"
        :title="collapsed ? item.label : undefined"
        @click="hasChildren(item) ? toggleExpand(item.key) : handleSelect(item)"
      >
        <component
          :is="item.icon"
          v-if="item.icon"
          class="size-4 shrink-0"
        />
        <span v-if="!collapsed" class="flex-1 text-left">{{ item.label }}</span>
      </button>
    </template>
  </nav>
</template>
