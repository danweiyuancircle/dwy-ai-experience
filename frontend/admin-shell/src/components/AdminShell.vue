<!--
  管理系统外壳（可复用）
  基于 eui EAdminLayout：侧栏菜单（可含子菜单）+ 顶栏扩展槽 + PageHero + router-view。
  折叠状态持久化；activeKey 支持 meta.menuKey。
  logo/标题区域可配置 logoTo，点击跳转（默认 /）。
  鉴权 / 业务顶栏：#header-center（公告等）+ #header-extra（套餐 / 用户）。
-->
<script setup lang="ts">
import { EAdminLayout } from '@dwydev/eui'
import type { MenuItem } from '@dwydev/eui'
import { useStorage } from '@dwydev/ekit'
import {
  DEFAULT_COLLAPSED_STORAGE_KEY,
  DEFAULT_LOGO_TO,
  DEFAULT_PAGE_HERO,
} from '../model/constants'
import { useAdminActiveKey } from '../composables/useAdminActiveKey'
import AdminPageHero from './AdminPageHero.vue'

const props = withDefaults(
  defineProps<{
    /** 左上角系统标题。示例：`宽舟科技` */
    title: string
    /** 左上角 logo。示例：`/logo.png` */
    logo?: string
    /**
     * 点击 logo/标题跳转的 path。
     * 默认 `/`；空字符串关闭点击。示例：`/dashboard`
     */
    logoTo?: string
    /** 侧栏菜单（可含 children）。 */
    menuItems: MenuItem[]
    /**
     * 折叠状态 localStorage key。
     * 默认 `admin:sidebar:collapsed`。
     */
    collapsedStorageKey?: string
    /**
     * 是否默认渲染 PageHero。
     * 默认 true；单页可用 meta.pageHero=false 关闭。
     */
    pageHero?: boolean
  }>(),
  {
    logoTo: DEFAULT_LOGO_TO,
    collapsedStorageKey: DEFAULT_COLLAPSED_STORAGE_KEY,
    pageHero: DEFAULT_PAGE_HERO,
  },
)

/** 侧栏折叠 — 跨会话保留用户偏好 */
const collapsed = useStorage(props.collapsedStorageKey, false)

/** 当前激活菜单 key */
const activeKey = useAdminActiveKey()

/** 是否渲染可点击 logo（非空 path） */
const isLogoLink = () => !!props.logoTo
</script>

<template>
  <EAdminLayout
    :title="title"
    :logo="logo"
    :menu-items="menuItems"
    :active-key="activeKey"
    v-model:collapsed="collapsed"
    router
  >
    <!-- 覆盖默认 logo 区：整块可点，折叠时仅图标仍可点 -->
    <template #logo>
      <router-link
        v-if="isLogoLink()"
        :to="logoTo"
        class="flex min-w-0 flex-1 items-center gap-2 rounded-md text-foreground no-underline outline-none transition-opacity hover:opacity-80 focus-visible:ring-2 focus-visible:ring-ring"
      >
        <img
          v-if="logo"
          :src="logo"
          class="h-7 w-7 shrink-0 object-contain"
          alt=""
        />
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
          class="h-7 w-7 shrink-0 object-contain"
          alt=""
        />
        <span
          v-if="title && !collapsed"
          class="truncate text-sm font-semibold"
        >
          {{ title }}
        </span>
      </template>
    </template>

    <template #header>
      <!--
        整段 pointer-events-none：中间空槽即使叠到汉堡上也不挡点击。
        公告自己打开指针；右侧套餐/用户菜单保持可点。
      -->
      <div class="pointer-events-none flex min-w-0 flex-1 items-center gap-3">
        <div
          data-slot="admin-header-center"
          class="min-w-0 flex-1 overflow-hidden"
        >
          <slot name="header-center" />
        </div>
        <div
          data-slot="admin-header-extra"
          class="pointer-events-auto ml-auto flex shrink-0 items-center gap-2"
        >
          <slot name="header-extra" />
        </div>
      </div>
    </template>

    <!--
      上下分区：main 不整体滚（见下方 :deep 样式）。
      上：PageHero 固定；下：业务页可自管滚动（因子看板等）或由本层 overflow-y-auto 滚动。
    -->
    <div class="flex h-full min-h-0 flex-1 flex-col">
      <!-- 上：页面标题（固定，不随业务内容滚动） -->
      <AdminPageHero :enabled="pageHero" />
      <!-- 下：业务页；min-h-0 才能让子页 h-full + 内部滚动生效 -->
      <div class="min-h-0 flex-1 overflow-y-auto">
        <router-view />
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
