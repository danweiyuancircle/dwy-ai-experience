<!--
  @dwydev/admin-kit 全屏预览宿主
  模拟「登录后」控制台：骨架 chrome 全开 + modules 子菜单。
  不依赖业务鉴权，user/notifications 用本地 mock。
-->
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BarChart3,
  KeyRound,
  LayoutDashboard,
  Settings,
  Users,
} from 'lucide-vue-next'
import { EBadge } from '@dwydev/eui'
import {
  AdminShell,
  asMenuIcon,
  createAdminShell,
  defineAdminModule,
  type AdminNotificationItem,
  type AdminUserInfo,
} from '@dwydev/admin-kit'

const router = useRouter()

/**
 * 仅用 createAdminShell 产菜单/props；路由由 router 嵌套 children 提供
 * （与 quant-cloud 扁平 routes 模式不同，方便 playground 单入口预览）
 */
const { shellProps } = createAdminShell({
  title: 'Demo Admin',
  logoTo: '/admin/dashboard',
  collapsedStorageKey: 'playground:dwy-admin:collapsed',
  pageHero: true,
  features: {
    theme: true,
    notifications: true,
    userMenu: true,
  },
  modules: [
    defineAdminModule({
      id: 'dashboard',
      order: 10,
      menu: {
        key: '/admin/dashboard',
        label: '数据概览',
        icon: asMenuIcon(LayoutDashboard),
      },
      routes: [],
    }),
    defineAdminModule({
      id: 'ops',
      order: 20,
      menu: {
        key: 'group-ops',
        label: '运营',
        icon: asMenuIcon(Users),
        children: [
          { key: '/admin/ops/users', label: '用户列表' },
          { key: '/admin/ops/plans', label: '套餐管理' },
        ],
      },
      routes: [],
    }),
    defineAdminModule({
      id: 'quota',
      order: 30,
      menu: {
        key: '/admin/quota',
        label: '用量统计',
        icon: asMenuIcon(BarChart3),
      },
      routes: [],
    }),
    defineAdminModule({
      id: 'keys',
      order: 40,
      menu: {
        key: '/admin/keys',
        label: 'API Key',
        icon: asMenuIcon(KeyRound),
      },
      routes: [],
    }),
    defineAdminModule({
      id: 'settings',
      order: 50,
      menu: {
        key: '/admin/settings',
        label: '个人设置',
        icon: asMenuIcon(Settings),
      },
      routes: [],
    }),
  ],
})

/** mock 用户 — 真实业务接 auth store */
const user = ref<AdminUserInfo>({
  name: '张三',
  email: 'zhangsan@example.com',
  roleLabel: '管理员',
})

/** mock 通知 */
const notifications = ref<AdminNotificationItem[]>([
  {
    id: '1',
    title: '套餐将于 7 天后到期',
    description: '请及时续费以免服务中断',
    time: '2 小时前',
    unread: true,
  },
  {
    id: '2',
    title: '导出任务已完成',
    description: 'factor_export_2026.csv 可下载',
    time: '昨天',
    unread: true,
  },
  {
    id: '3',
    title: '新功能：因子看板',
    description: '可在侧栏「用量」旁找到入口（示例）',
    time: '3 天前',
    unread: false,
  },
])

function onLogout() {
  // 预览：回门户首页
  router.push('/')
}
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-background">
    <AdminShell
      v-bind="shellProps"
      :user="user"
      :notifications="notifications"
      profile-path="/admin/settings"
      notifications-path="/admin/dashboard"
      @logout="onLogout"
    >
      <template #header-extra>
        <EBadge variant="outline" class="mr-1 gap-1 text-xs">
          预览
        </EBadge>
      </template>
    </AdminShell>
  </div>
</template>
