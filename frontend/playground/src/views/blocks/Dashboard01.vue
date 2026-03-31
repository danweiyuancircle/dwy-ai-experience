<script setup lang="ts">
import {
  LayoutDashboard,
  Users,
  CreditCard,
  Activity,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-vue-next'

const stats = [
  {
    title: '总收入',
    value: '¥45,231.89',
    change: '+20.1%',
    trend: 'up',
    description: '较上月',
    icon: DollarSign,
  },
  {
    title: '订阅数',
    value: '+2,350',
    change: '+180.1%',
    trend: 'up',
    description: '较上月',
    icon: Users,
  },
  {
    title: '销售额',
    value: '+12,234',
    change: '+19%',
    trend: 'up',
    description: '较上月',
    icon: CreditCard,
  },
  {
    title: '活跃用户',
    value: '+573',
    change: '-2.5%',
    trend: 'down',
    description: '较上月',
    icon: Activity,
  },
]

const tableColumns = [
  { key: 'name', title: '客户', width: 180 },
  { key: 'email', title: '邮箱' },
  { key: 'amount', title: '金额', align: 'right' as const, width: 120 },
]

const tableData = [
  { id: 1, name: '李明', email: 'liming@example.com', amount: '¥1,999.00' },
  { id: 2, name: '王芳', email: 'wangfang@example.com', amount: '¥39.00' },
  { id: 3, name: '张伟', email: 'zhangwei@example.com', amount: '¥299.00' },
  { id: 4, name: '刘洋', email: 'liuyang@example.com', amount: '¥99.00' },
  { id: 5, name: '陈静', email: 'chenjing@example.com', amount: '¥2,500.00' },
]

const navItems = [
  { label: '概览', icon: LayoutDashboard, active: true },
  { label: '客户', icon: Users, active: false },
  { label: '交易', icon: CreditCard, active: false },
  { label: '活动', icon: Activity, active: false },
]
</script>

<template>
  <div class="h-[calc(100vh-8rem)] rounded-lg border overflow-hidden flex bg-background">
    <!-- Left Sidebar Nav -->
    <aside class="hidden w-60 shrink-0 border-r bg-muted/30 md:block">
      <div class="flex h-16 items-center border-b px-6">
        <LayoutDashboard class="mr-2 size-5 text-primary" />
        <span class="text-lg font-semibold">DashBoard</span>
      </div>
      <nav class="flex flex-col gap-1 p-4">
        <a
          v-for="item in navItems"
          :key="item.label"
          href="#"
          class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
          :class="
            item.active
              ? 'bg-primary text-primary-foreground font-medium'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          "
        >
          <component :is="item.icon" class="size-4" />
          {{ item.label }}
        </a>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <!-- Header -->
      <header class="flex h-16 items-center justify-between border-b px-6">
        <div>
          <h1 class="text-xl font-semibold">Dashboard</h1>
          <p class="text-xs text-muted-foreground">2026-01-01 至 2026-03-31</p>
        </div>
        <EButton variant="outline" size="sm">下载报告</EButton>
      </header>

      <div class="p-6 space-y-6">
        <!-- Stats Row -->
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <ECard v-for="stat in stats" :key="stat.title">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-muted-foreground">{{ stat.title }}</p>
              <component :is="stat.icon" class="size-4 text-muted-foreground" />
            </div>
            <div class="mt-2">
              <div class="text-2xl font-bold">{{ stat.value }}</div>
              <p class="mt-1 flex items-center text-xs text-muted-foreground">
                <span
                  class="inline-flex items-center font-medium"
                  :class="stat.trend === 'up' ? 'text-green-600' : 'text-red-500'"
                >
                  <ArrowUpRight v-if="stat.trend === 'up'" class="mr-0.5 size-3" />
                  <ArrowDownRight v-else class="mr-0.5 size-3" />
                  {{ stat.change }}
                </span>
                <span class="ml-1">{{ stat.description }}</span>
              </p>
            </div>
          </ECard>
        </div>

        <!-- Chart + Recent Sales Row -->
        <div class="grid gap-4 lg:grid-cols-7">
          <!-- Chart Placeholder -->
          <ECard title="概览" class="lg:col-span-4">
            <div
              class="bg-muted rounded-md h-[300px] flex items-center justify-center"
            >
              <p class="text-muted-foreground text-sm">图表区域</p>
            </div>
          </ECard>

          <!-- Recent Sales -->
          <ECard title="近期销售" description="本月共完成 265 笔交易" class="lg:col-span-3">
            <div class="space-y-4">
              <div
                v-for="row in tableData"
                :key="row.id"
                class="flex items-center justify-between"
              >
                <div class="flex items-center gap-3">
                  <EAvatar
                    :alt="row.name"
                    :fallback="row.name.charAt(0)"
                    size="sm"
                  />
                  <div>
                    <p class="text-sm font-medium leading-none">{{ row.name }}</p>
                    <p class="text-xs text-muted-foreground mt-0.5">{{ row.email }}</p>
                  </div>
                </div>
                <span class="text-sm font-medium">{{ row.amount }}</span>
              </div>
            </div>
          </ECard>
        </div>

        <!-- Table Area -->
        <ECard title="近期交易" description="最近 5 笔交易记录">
          <ETable :data="tableData" :columns="tableColumns" />
        </ECard>
      </div>
    </main>
  </div>
</template>
