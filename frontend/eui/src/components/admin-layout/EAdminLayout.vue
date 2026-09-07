<!--
  EAdminLayout 管理后台布局组件
  提供"侧边栏 + 顶部 + 主内容 + 底部"的后台通用结构
  桌面：侧栏占位，汉堡切换 collapsed。
  手机（默认 drawer）：侧栏不占宽，汉堡打开左侧 ESheet；collapsed 与抽屉状态独立。
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Menu } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useEuiMobile } from '@/composables/useEuiMobile'
import { EMenu } from '../menu'
import { ESheet } from '../sheet'
import type { EAdminLayoutProps, EAdminLayoutEmits } from './types'

const props = withDefaults(defineProps<EAdminLayoutProps>(), {
  menuItems: () => [],
  collapsed: false,
  showFooter: false,
  headerHeight: 56,
  sidebarWidth: 240,
  collapsedWidth: 56,
  mobileMode: 'drawer',
})

const emit = defineEmits<EAdminLayoutEmits>()

/** 是否处于手机断点。mobileBreakpoint 可覆盖全局配置 */
const isMobile = useEuiMobile(() => props.mobileBreakpoint)

/** 真正走抽屉：窄屏且未关闭该能力 */
const isDrawerLayout = computed(() => isMobile.value && props.mobileMode === 'drawer')

/** 抽屉开关：受控 mobileOpen 优先，否则本地状态 */
const localMobileOpen = ref(false)
const mobileOpenModel = computed({
  get: () => props.mobileOpen ?? localMobileOpen.value,
  set: (value: boolean) => {
    localMobileOpen.value = value
    emit('update:mobileOpen', value)
  },
})

// 将数字形式的宽度转为 px 字符串，方便直接写入 style
const sidebarWidthPx = computed(() => {
  const w = props.collapsed ? props.collapsedWidth : props.sidebarWidth
  return typeof w === 'number' ? `${w}px` : w
})

// 将数字形式的高度转为 px 字符串
const headerHeightPx = computed(() => {
  const h = props.headerHeight
  return typeof h === 'number' ? `${h}px` : h
})

/**
 * 菜单点击处理：同时派发 activeKey 更新与语义化的 menu-select 事件。
 * 抽屉里点菜单后关掉 Sheet，避免挡住内容。
 */
function handleMenuSelect(key: string) {
  emit('update:activeKey', key)
  emit('menu-select', key)
  if (isDrawerLayout.value) {
    mobileOpenModel.value = false
  }
}

/**
 * 顶栏汉堡：桌面切折叠，手机切抽屉。两套状态互不写入。
 * 抽屉必须等当前 pointer 事件结束再开：汉堡在 Dialog 外面，同一手势会被
 * reka Dialog 当成 pointer-down-outside，刚打开就关掉。
 */
function handleTrigger(event?: Event) {
  event?.stopPropagation()
  if (isDrawerLayout.value) {
    const next = !mobileOpenModel.value
    queueMicrotask(() => {
      mobileOpenModel.value = next
    })
    return
  }
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <div
    data-slot="admin-layout"
    :class="cn('flex h-screen w-full overflow-hidden bg-background', props.class)"
  >
    <!-- 桌面占位侧栏 -->
    <aside
      v-if="!isDrawerLayout"
      data-slot="admin-layout-sidebar"
      :style="{ width: sidebarWidthPx }"
      class="flex shrink-0 flex-col overflow-hidden border-r bg-background transition-[width] duration-200"
    >
      <div
        :style="{ height: headerHeightPx }"
        class="flex shrink-0 items-center gap-2 border-b px-4"
      >
        <slot name="logo">
          <img v-if="logo" :src="logo" class="h-7 w-7 shrink-0 object-contain" alt="logo">
          <span v-if="title && !collapsed" class="truncate text-sm font-semibold">{{ title }}</span>
        </slot>
      </div>

      <div class="flex-1 overflow-y-auto py-2">
        <slot name="sidebar">
          <EMenu
            :items="menuItems"
            :model-value="activeKey"
            :collapsed="collapsed"
            :router="router"
            @update:model-value="handleMenuSelect"
          />
        </slot>
      </div>

      <div v-if="$slots['sidebar-footer']" class="border-t p-2">
        <slot name="sidebar-footer" />
      </div>
    </aside>

    <!-- 手机：侧栏进左侧抽屉，不占主栏宽度 -->
    <ESheet
      v-else
      :open="mobileOpenModel"
      side="left"
      body-class="p-0"
      @update:open="mobileOpenModel = $event"
    >
      <div
        data-slot="admin-layout-sidebar"
        class="flex h-full min-h-0 flex-col"
      >
        <div
          :style="{ height: headerHeightPx }"
          class="flex shrink-0 items-center gap-2 border-b px-4"
        >
          <slot name="logo">
            <img v-if="logo" :src="logo" class="h-7 w-7 shrink-0 object-contain" alt="logo">
            <span v-if="title" class="truncate text-sm font-semibold">{{ title }}</span>
          </slot>
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto py-2">
          <slot name="sidebar">
            <EMenu
              :items="menuItems"
              :model-value="activeKey"
              :collapsed="false"
              :router="router"
              @update:model-value="handleMenuSelect"
            />
          </slot>
        </div>
        <div v-if="$slots['sidebar-footer']" class="border-t p-2">
          <slot name="sidebar-footer" />
        </div>
      </div>
    </ESheet>

    <!-- Main area -->
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <!-- Header -->
      <header
        data-slot="admin-layout-header"
        :style="{ height: headerHeightPx }"
        class="flex shrink-0 items-center gap-4 border-b bg-background px-4"
      >
        <button
          type="button"
          data-slot="admin-layout-sidebar-trigger"
          class="relative z-10 flex size-11 shrink-0 items-center justify-center rounded-md outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/50"
          :aria-expanded="isDrawerLayout ? mobileOpenModel : !collapsed"
          @pointerdown.stop
          @click.stop="handleTrigger"
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
