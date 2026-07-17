<!--
  管理系统外壳（可复用）
  基于 eui EAdminLayout：侧栏菜单（可含子菜单）+ 顶栏扩展槽 + PageHero + router-view。
  折叠状态持久化；activeKey 支持 meta.menuKey。
  鉴权 / 业务顶栏内容由宿主通过 #header-extra 注入。
-->
<script setup lang="ts">
import { EAdminLayout } from '@dwydev/eui'
import type { MenuItem } from '@dwydev/eui'
import { useStorage } from '@dwydev/ekit'
import { DEFAULT_COLLAPSED_STORAGE_KEY, DEFAULT_PAGE_HERO } from '../model/constants'
import { useAdminActiveKey } from '../composables/useAdminActiveKey'
import AdminPageHero from './AdminPageHero.vue'

const props = withDefaults(
  defineProps<{
    /** 左上角系统标题。示例：`宽舟科技` */
    title: string
    /** 左上角 logo。示例：`/logo.png` */
    logo?: string
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
    collapsedStorageKey: DEFAULT_COLLAPSED_STORAGE_KEY,
    pageHero: DEFAULT_PAGE_HERO,
  },
)

/** 侧栏折叠 — 跨会话保留用户偏好 */
const collapsed = useStorage(props.collapsedStorageKey, false)

/** 当前激活菜单 key */
const activeKey = useAdminActiveKey()
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
    <template #header>
      <div class="ml-auto flex items-center gap-2">
        <slot name="header-extra" />
      </div>
    </template>

    <AdminPageHero :enabled="pageHero" />
    <router-view />
  </EAdminLayout>
</template>
