<script setup lang="ts">
import { ref } from 'vue'
import {
  SquareTerminal,
  Bot,
  BookOpen,
  Settings2,
  Frame,
  PieChart,
  Map,
  ChevronRight,
  ChevronsUpDown,
  AudioWaveform,
  GalleryVerticalEnd,
} from 'lucide-vue-next'

const navMain = [
  {
    title: 'Playground',
    icon: SquareTerminal,
    isActive: true,
    items: [
      { title: '历史记录', href: '#' },
      { title: '收藏', href: '#' },
      { title: '设置', href: '#' },
    ],
  },
  {
    title: 'Models',
    icon: Bot,
    items: [
      { title: 'Genesis', href: '#' },
      { title: 'Explorer', href: '#' },
      { title: 'Quantum', href: '#' },
    ],
  },
  {
    title: 'Documentation',
    icon: BookOpen,
    items: [
      { title: '介绍', href: '#' },
      { title: '快速开始', href: '#' },
      { title: '教程', href: '#' },
      { title: '变更日志', href: '#' },
    ],
  },
  {
    title: 'Settings',
    icon: Settings2,
    items: [
      { title: '常规', href: '#' },
      { title: '团队', href: '#' },
      { title: '计费', href: '#' },
      { title: '用量限制', href: '#' },
    ],
  },
]

const navProjects = [
  { title: 'Design Engineering', icon: Frame, href: '#' },
  { title: 'Sales & Marketing', icon: PieChart, href: '#' },
  { title: 'Travel', icon: Map, href: '#' },
]

const openMap = ref<Record<string, boolean>>({
  Playground: true,
})

function toggleCollapsible(title: string) {
  openMap.value[title] = !openMap.value[title]
}

const dropdownItems = [
  { key: 'account', label: '账号设置' },
  { key: 'billing', label: '计费管理' },
  { key: 'notifications', label: '通知偏好', divided: true },
  { key: 'logout', label: '退出登录', variant: 'destructive' as const },
]

const teamDropdownItems = [
  { key: 'acme-inc', label: 'Acme Inc' },
  { key: 'acme-corp', label: 'Acme Corp.' },
  { key: 'evil-corp', label: 'Evil Corp.' },
]
</script>

<template>
  <div class="h-[calc(100vh-8rem)] rounded-lg border overflow-hidden">
  <ESidebarProvider class="!min-h-0 h-full">
    <ESidebar collapsible="icon">
      <!-- Sidebar Header: Team Switcher -->
      <ESidebarHeader>
        <ESidebarMenu>
          <ESidebarMenuItem>
            <EDropdown :items="teamDropdownItems" side="bottom" align="start">
              <ESidebarMenuButton
                size="lg"
                tooltip="Acme Inc"
                class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <div
                  class="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg"
                >
                  <GalleryVerticalEnd class="size-4" />
                </div>
                <div class="grid flex-1 text-left text-sm leading-tight">
                  <span class="truncate font-semibold">Acme Inc</span>
                  <span class="truncate text-xs">企业版</span>
                </div>
                <ChevronsUpDown class="ml-auto" />
              </ESidebarMenuButton>
            </EDropdown>
          </ESidebarMenuItem>
        </ESidebarMenu>
      </ESidebarHeader>

      <!-- Sidebar Content -->
      <ESidebarContent>
        <!-- Platform Group -->
        <ESidebarGroup>
          <ESidebarGroupLabel>Platform</ESidebarGroupLabel>
          <ESidebarGroupContent>
            <ESidebarMenu>
              <ESidebarMenuItem v-for="item in navMain" :key="item.title">
                <ECollapsible
                  :model-value="!!openMap[item.title]"
                  @update:model-value="toggleCollapsible(item.title)"
                  class="group/collapsible"
                >
                  <template #trigger>
                    <ESidebarMenuButton :tooltip="item.title">
                      <component :is="item.icon" />
                      <span>{{ item.title }}</span>
                      <ChevronRight
                        class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                      />
                    </ESidebarMenuButton>
                  </template>

                  <ul class="ml-4 border-l border-sidebar-border pl-2 mt-1 space-y-1">
                    <li v-for="sub in item.items" :key="sub.title">
                      <a
                        :href="sub.href"
                        class="flex h-7 items-center rounded-md px-2 text-sm text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                      >
                        {{ sub.title }}
                      </a>
                    </li>
                  </ul>
                </ECollapsible>
              </ESidebarMenuItem>
            </ESidebarMenu>
          </ESidebarGroupContent>
        </ESidebarGroup>

        <!-- Projects Group -->
        <ESidebarGroup>
          <ESidebarGroupLabel>Projects</ESidebarGroupLabel>
          <ESidebarGroupContent>
            <ESidebarMenu>
              <ESidebarMenuItem v-for="item in navProjects" :key="item.title">
                <ESidebarMenuButton :tooltip="item.title" as="a" :href="item.href">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </ESidebarMenuButton>
              </ESidebarMenuItem>
            </ESidebarMenu>
          </ESidebarGroupContent>
        </ESidebarGroup>
      </ESidebarContent>

      <!-- Sidebar Footer: User -->
      <ESidebarFooter>
        <ESidebarMenu>
          <ESidebarMenuItem>
            <EDropdown :items="dropdownItems" side="top" align="start">
              <ESidebarMenuButton
                size="lg"
                tooltip="用户菜单"
                class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <EAvatar
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                  alt="用户头像"
                  size="sm"
                  class="size-8 rounded-lg"
                />
                <div class="grid flex-1 text-left text-sm leading-tight">
                  <span class="truncate font-semibold">张三</span>
                  <span class="truncate text-xs">zhangsan@example.com</span>
                </div>
                <ChevronsUpDown class="ml-auto size-4" />
              </ESidebarMenuButton>
            </EDropdown>
          </ESidebarMenuItem>
        </ESidebarMenu>
      </ESidebarFooter>
    </ESidebar>

    <!-- Main Content Area -->
    <main class="flex flex-1 flex-col">
      <!-- Header Bar -->
      <header class="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <ESidebarTrigger class="-ml-1" />
        <ESeparator orientation="vertical" class="mr-2 !h-4" />
        <EBreadcrumb
          :items="[
            { label: '工作台', href: '#' },
            { label: 'Playground', href: '#' },
            { label: '历史记录' },
          ]"
        />
      </header>

      <!-- Page Content -->
      <div class="flex-1 p-6 space-y-6">
        <!-- Top Cards Row -->
        <div class="grid gap-4 md:grid-cols-3">
          <ECard title="总请求数" description="过去 30 天">
            <div class="text-3xl font-bold">12,453</div>
          </ECard>
          <ECard title="成功率" description="过去 30 天">
            <div class="text-3xl font-bold text-green-600">99.8%</div>
          </ECard>
          <ECard title="平均延迟" description="过去 30 天">
            <div class="text-3xl font-bold">142ms</div>
          </ECard>
        </div>

        <!-- Large Placeholder Area -->
        <ECard title="模型输出" description="实时预览区域">
          <div
            class="bg-muted/50 rounded-xl border border-dashed flex min-h-[400px] items-center justify-center"
          >
            <p class="text-muted-foreground text-sm">内容区域占位</p>
          </div>
        </ECard>
      </div>
    </main>
  </ESidebarProvider>
  </div>
</template>
