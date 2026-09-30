<!--
  @dwydev/admin-kit 全屏预览宿主
  模拟「登录后」控制台：壳 + modules 菜单;用户菜单经 header-extra 插槽
  由宿主自行组装(0.2.0 起不再内置 chrome,与 quant-cloud 用法一致)。
  不依赖业务鉴权,用户信息用本地 mock。
-->
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BarChart3,
  KeyRound,
  LayoutDashboard,
  LogOut,
  Settings,
  User,
  Users,
} from 'lucide-vue-next'
import { EBadge, EDropdown } from '@dwydev/eui'
import {
  AdminShell,
  asMenuIcon,
  createAdminShell,
  defineAdminModule,
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
const userName = ref('张三')

/** 退出登录:预览回门户首页 */
function onLogout() {
  router.push('/')
}
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-background">
    <AdminShell v-bind="shellProps">
      <template #header-center>
        <span class="hidden text-xs text-muted-foreground md:inline">
          @dwydev/admin-kit 0.2.0 预览
        </span>
      </template>
      <template #header-extra>
        <EBadge variant="outline" class="mr-1 gap-1 text-xs">
          预览
        </EBadge>
        <!-- 用户菜单由宿主组装(示例);真实业务在此接 auth store 的用户下拉 -->
        <EDropdown
          :items="[
            { key: 'profile', label: '个人设置', icon: User },
            { key: 'logout', label: '退出登录', icon: LogOut },
          ]"
          @select="(key: string) => key === 'logout' && onLogout()"
        >
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted"
          >
            <span
              class="inline-flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary"
            >
              {{ userName[0] }}
            </span>
            {{ userName }}
          </button>
        </EDropdown>
      </template>
    </AdminShell>
  </div>
</template>
