<!--
  通用后台管理系统骨架（基于 @dwydev/eui）
  布局：EAdminLayout + EMenu
  顶栏 chrome：EButton / EAvatar / EDropdown / EPopover / useTheme
  业务：modules 菜单扩展；#header-extra 插业务徽章
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bell,
  LayoutDashboard,
  LogOut,
  Moon,
  Settings,
  Sun,
} from 'lucide-vue-next'
import {
  EAdminLayout,
  EAvatar,
  EButton,
  EDropdown,
  EPopover,
  useTheme,
  type DropdownMenuItem,
  type MenuItem,
} from '@dwydev/eui'
import { useStorage } from '@dwydev/ekit'
import { resolveFeatures } from '../create-admin-shell'
import {
  DEFAULT_COLLAPSED_STORAGE_KEY,
  DEFAULT_LOGO_TO,
  DEFAULT_PAGE_HERO,
} from '../model/constants'
import type {
  AdminNotificationItem,
  AdminShellFeatures,
  AdminUserInfo,
  AdminUserMenuItem,
} from '../model/types'
import { useAdminActiveKey } from '../composables/useAdminActiveKey'
import AdminPageHero from './AdminPageHero.vue'

const props = withDefaults(
  defineProps<{
    /** 左上角系统标题 */
    title: string
    /** 左上角 logo */
    logo?: string
    /**
     * 点击 logo 跳转 path。
     * 默认 `/`；空字符串关闭点击。
     */
    logoTo?: string
    /** 侧栏菜单（可含 children） */
    menuItems: MenuItem[]
    /** 折叠状态 localStorage key */
    collapsedStorageKey?: string
    /** 是否默认渲染 PageHero */
    pageHero?: boolean
    /** 功能开关 */
    features?: AdminShellFeatures
    /** 当前用户（userMenu 开启时） */
    user?: AdminUserInfo | null
    /** 通知列表 */
    notifications?: AdminNotificationItem[]
    /** 用户下拉扩展项（退出前） */
    userMenuItems?: AdminUserMenuItem[]
    /** 个人中心 path */
    profilePath?: string
    /** 通知「查看全部」path */
    notificationsPath?: string
  }>(),
  {
    logoTo: DEFAULT_LOGO_TO,
    collapsedStorageKey: DEFAULT_COLLAPSED_STORAGE_KEY,
    pageHero: DEFAULT_PAGE_HERO,
    user: null,
    notifications: () => [],
    userMenuItems: () => [],
    profilePath: '/settings',
  },
)

const emit = defineEmits<{
  /** 点击退出登录 */
  logout: []
  /** 用户菜单项选中 */
  'user-action': [key: string]
  /** 通知项点击 */
  'notification-click': [item: AdminNotificationItem]
  /** 查看全部通知 */
  'notifications-view-all': []
}>()

const router = useRouter()
const { isDark, toggleDark } = useTheme()

/** 解析后的功能开关 */
const feat = computed(() => resolveFeatures(props.features))

/** 侧栏折叠 — 跨会话保留 */
const collapsed = useStorage(props.collapsedStorageKey, false)

/** 当前激活菜单 key */
const activeKey = useAdminActiveKey()

/** 是否渲染可点击 logo */
const logoClickable = computed(() => !!props.logoTo)

/**
 * 通知红点：有 unread===true 显示；全部未声明 unread 且列表非空也显示。
 */
const showNotifDot = computed(() => {
  const list = props.notifications ?? []
  if (list.length === 0) return false
  if (list.some((n) => n.unread === true)) return true
  return list.every((n) => n.unread === undefined)
})

/** 头像 fallback：取 name 首字 */
const avatarFallback = computed(() => {
  const name = props.user?.name?.trim()
  return name ? name.charAt(0).toUpperCase() : 'U'
})

/** 用户下拉菜单 items（图标用 lucide 组件，EDropdown 支持） */
const userDropdownItems = computed<DropdownMenuItem[]>(() => {
  const extras: DropdownMenuItem[] = (props.userMenuItems ?? []).map((item) => ({
    key: item.key,
    label: item.label,
    variant: item.destructive ? 'destructive' : 'default',
  }))
  return [
    { key: '__home', label: '控制台首页', icon: LayoutDashboard },
    { key: '__profile', label: '个人中心', icon: Settings },
    ...extras,
    { key: '__logout', label: '退出登录', icon: LogOut, divided: true, variant: 'destructive' },
  ]
})

/**
 * 用户菜单选中
 * 内置 key：__home / __profile / __logout；其余按 to 跳转。
 */
function onUserSelect(key: string) {
  emit('user-action', key)
  if (key === '__home') {
    if (props.logoTo) router.push(props.logoTo)
    return
  }
  if (key === '__profile') {
    router.push(props.profilePath)
    return
  }
  if (key === '__logout') {
    emit('logout')
    return
  }
  const item = props.userMenuItems?.find((i) => i.key === key)
  if (item?.to) router.push(item.to)
}

/** 通知项点击 */
function onNotifClick(item: AdminNotificationItem) {
  emit('notification-click', item)
}

/** 查看全部通知 */
function onViewAll() {
  emit('notifications-view-all')
  if (props.notificationsPath) router.push(props.notificationsPath)
}
</script>

<template>
  <EAdminLayout
    :title="title"
    :logo="logo"
    :menu-items="menuItems"
    :active-key="activeKey"
    v-model:collapsed="collapsed"
    router
    class="bg-background text-foreground"
  >
    <!-- 品牌区：可配置跳转首页 -->
    <template #logo>
      <router-link
        v-if="logoClickable"
        :to="logoTo"
        class="flex min-w-0 flex-1 items-center gap-2 rounded-md text-foreground no-underline outline-none transition-opacity hover:opacity-80 focus-visible:ring-[3px] focus-visible:ring-ring/50"
      >
        <img
          v-if="logo"
          :src="logo"
          class="size-7 shrink-0 rounded-md object-contain"
          alt=""
        >
        <span
          v-if="title && !collapsed"
          class="truncate text-sm font-semibold"
        >
          {{ title }}
        </span>
      </router-link>
      <template v-else>
        <img
          v-if="logo"
          :src="logo"
          class="size-7 shrink-0 rounded-md object-contain"
          alt=""
        >
        <span
          v-if="title && !collapsed"
          class="truncate text-sm font-semibold"
        >
          {{ title }}
        </span>
      </template>
    </template>

    <template #header>
      <div class="ml-auto flex items-center gap-1" data-slot="admin-header-tools">
        <!-- 宿主业务扩展（套餐徽章等） -->
        <slot name="header-extra" />

        <!-- 主题：EButton ghost icon -->
        <EButton
          v-if="feat.theme"
          type="button"
          variant="ghost"
          size="icon-sm"
          :aria-label="isDark ? '切换到亮色' : '切换到暗色'"
          data-slot="admin-theme-toggle"
          @click="toggleDark()"
        >
          <Sun v-if="isDark" class="size-4" />
          <Moon v-else class="size-4" />
        </EButton>

        <!-- 通知：EPopover + EButton 触发 -->
        <EPopover
          v-if="feat.notifications"
          align="end"
          :side-offset="8"
          class="w-72 rounded-xl p-0"
          data-slot="admin-notifications"
        >
          <template #trigger>
            <EButton
              type="button"
              variant="ghost"
              size="icon-sm"
              class="relative"
              aria-label="通知"
            >
              <Bell class="size-4" />
              <span
                v-if="showNotifDot"
                class="absolute top-1.5 right-1.5 size-1.5 rounded-full bg-destructive ring-2 ring-background"
              />
            </EButton>
          </template>
          <div class="overflow-hidden rounded-xl">
            <div class="border-b border-border px-3 py-2.5">
              <div class="text-sm font-semibold">
                通知
              </div>
              <div class="text-xs text-muted-foreground">
                {{ notifications?.length ? `${notifications.length} 条` : '暂无新通知' }}
              </div>
            </div>
            <div class="max-h-64 overflow-y-auto py-1">
              <button
                v-for="item in notifications"
                :key="item.id"
                type="button"
                class="flex w-full flex-col gap-0.5 rounded-md px-3 py-2.5 text-left transition-colors hover:bg-accent"
                @click="onNotifClick(item)"
              >
                <span class="text-sm font-medium leading-snug">{{ item.title }}</span>
                <span
                  v-if="item.description"
                  class="line-clamp-2 text-xs text-muted-foreground"
                >{{ item.description }}</span>
                <span
                  v-if="item.time"
                  class="text-[11px] text-muted-foreground/80"
                >{{ item.time }}</span>
              </button>
              <div
                v-if="!notifications?.length"
                class="px-3 py-8 text-center text-sm text-muted-foreground"
              >
                暂无通知
              </div>
            </div>
            <div
              v-if="notificationsPath"
              class="border-t border-border p-1"
            >
              <EButton
                type="button"
                variant="ghost"
                size="sm"
                class="w-full"
                @click="onViewAll"
              >
                查看全部
              </EButton>
            </div>
          </div>
        </EPopover>

        <!-- 用户：EDropdown + EAvatar + EButton 触发 -->
        <EDropdown
          v-if="feat.userMenu"
          :items="userDropdownItems"
          align="end"
          data-slot="admin-user-menu"
          @select="onUserSelect"
        >
          <EButton
            type="button"
            variant="ghost"
            size="sm"
            class="gap-2 px-1.5"
          >
            <EAvatar
              :src="user?.avatarUrl"
              :fallback="avatarFallback"
              size="sm"
              class="rounded-full"
            />
            <span
              v-if="user?.name"
              class="hidden max-w-[7rem] truncate text-sm font-normal sm:inline"
            >{{ user.name }}</span>
          </EButton>
        </EDropdown>

        <slot name="header-actions" />
      </div>
    </template>

    <!--
      上下分区：main 不整体滚。
      上：PageHero 固定；下：业务内容区（eui token 背景 + 圆角内容节奏由业务 ECard 承担）
    -->
    <div class="flex h-full min-h-0 flex-1 flex-col">
      <AdminPageHero :enabled="pageHero" />
      <div
        class="min-h-0 flex-1 overflow-y-auto"
        data-slot="admin-content"
      >
        <slot>
          <router-view />
        </slot>
      </div>
    </div>
  </EAdminLayout>
</template>

<style scoped>
/**
 * eui EAdminLayout 的 main 默认 overflow-auto，会导致 Hero+内容整页一起滚。
 * 改为 flex 列 + overflow:hidden，上 Hero 固定，下侧区域再滚。
 */
:deep([data-slot='admin-layout-content']) {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
</style>
