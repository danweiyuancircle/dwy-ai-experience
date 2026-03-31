<script setup lang="ts">
import { computed } from 'vue'
import { Menu } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { EMenu } from '../menu'
import type { EAdminLayoutProps, EAdminLayoutEmits } from './types'

const props = withDefaults(defineProps<EAdminLayoutProps>(), {
  menuItems: () => [],
  collapsed: false,
  showFooter: false,
  headerHeight: 56,
  sidebarWidth: 240,
  collapsedWidth: 56,
})

const emit = defineEmits<EAdminLayoutEmits>()

const sidebarWidthPx = computed(() => {
  const w = props.collapsed ? props.collapsedWidth : props.sidebarWidth
  return typeof w === 'number' ? `${w}px` : w
})

const headerHeightPx = computed(() => {
  const h = props.headerHeight
  return typeof h === 'number' ? `${h}px` : h
})

function handleMenuSelect(key: string) {
  emit('update:activeKey', key)
  emit('menu-select', key)
}

function toggleCollapsed() {
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <div
    data-slot="admin-layout"
    :class="cn('flex h-screen w-full overflow-hidden bg-background', props.class)"
  >
    <!-- Sidebar -->
    <aside
      data-slot="admin-layout-sidebar"
      :style="{ width: sidebarWidthPx }"
      class="flex flex-col border-r bg-background transition-[width] duration-200 overflow-hidden shrink-0"
    >
      <!-- Sidebar header / logo -->
      <div
        :style="{ height: headerHeightPx }"
        class="flex items-center gap-2 border-b px-4 shrink-0"
      >
        <slot name="logo">
          <img v-if="logo" :src="logo" class="h-7 w-7 shrink-0 object-contain" alt="logo" />
          <span v-if="title && !collapsed" class="font-semibold text-sm truncate">{{ title }}</span>
        </slot>
      </div>

      <!-- Navigation -->
      <div class="flex-1 overflow-y-auto py-2">
        <slot name="sidebar">
          <EMenu
            :items="menuItems"
            :model-value="activeKey"
            :collapsed="collapsed"
            @update:model-value="handleMenuSelect"
          />
        </slot>
      </div>

      <!-- Sidebar footer -->
      <div v-if="$slots['sidebar-footer']" class="border-t p-2">
        <slot name="sidebar-footer" />
      </div>
    </aside>

    <!-- Main area -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Header -->
      <header
        data-slot="admin-layout-header"
        :style="{ height: headerHeightPx }"
        class="flex items-center gap-4 border-b bg-background px-4 shrink-0"
      >
        <button
          type="button"
          class="rounded-md p-1.5 hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          @click="toggleCollapsed"
        >
          <Menu class="size-4" />
          <span class="sr-only">Toggle sidebar</span>
        </button>
        <slot name="header" />
      </header>

      <!-- Content -->
      <main
        data-slot="admin-layout-content"
        class="flex-1 overflow-auto p-4"
      >
        <slot />
      </main>

      <!-- Footer -->
      <footer
        v-if="showFooter || $slots.footer"
        data-slot="admin-layout-footer"
        class="border-t px-4 py-2 text-center text-xs text-muted-foreground"
      >
        <slot name="footer" />
      </footer>
    </div>
  </div>
</template>
