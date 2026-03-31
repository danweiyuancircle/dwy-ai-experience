<script setup lang="ts">
const moduleCards = [
  {
    title: 'EUI 组件',
    desc: 'Vue 3 组件库 — 基于 Reka-ui + shadcn-vue 风格 + Element Plus 式 API',
    path: '/eui',
    badge: '91+ 组件',
    badgeVariant: 'default' as const,
  },
  {
    title: 'Core 工具',
    desc: '前端通用工具库 — request / storage / validators / date / hooks',
    path: '/core',
    badge: '5 模块',
    badgeVariant: 'secondary' as const,
  },
  {
    title: 'Backend',
    desc: 'FastAPI 基础设施包 — 配置 / 数据库 / 安全 / 异常 / 响应 / 缓存',
    path: '/backend',
    badge: 'Python 3.11+',
    badgeVariant: 'secondary' as const,
  },
  {
    title: 'CLI',
    desc: 'create-dwy 项目脚手架 + Claude Code 配置同步工具',
    path: '/cli',
    badge: 'create-dwy',
    badgeVariant: 'outline' as const,
  },
  {
    title: 'Claude Code',
    desc: 'Skills / Rules / Hooks / Settings 配置管理',
    path: '/claude',
    badge: '配置同步',
    badgeVariant: 'outline' as const,
  },
]

const stats = [
  { label: 'EUI 组件', value: 89, suffix: '' },
  { label: 'Core 模块', value: 5, suffix: '' },
  { label: 'Backend 模块', value: 8, suffix: '' },
  { label: 'CLI 命令', value: 3, suffix: '' },
  { label: 'Claude Skills', value: 3, suffix: '' },
]
</script>

<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="mb-10">
      <h1 class="text-4xl font-bold mb-3">DWY Shared</h1>
      <p class="text-muted-foreground text-lg">
        共享基础包 Monorepo 文档门户
      </p>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-5 gap-4 mb-10">
      <div v-for="stat in stats" :key="stat.label" class="text-center">
        <EStatistic :title="stat.label" :value="stat.value" :suffix="stat.suffix" />
      </div>
    </div>

    <!-- Module Cards -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">模块</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <router-link
          v-for="card in moduleCards"
          :key="card.path"
          :to="card.path"
          class="block"
        >
          <ECard class="h-full hover:border-primary/50 transition-colors cursor-pointer">
            <div class="flex items-start justify-between mb-2">
              <div class="font-semibold text-base">{{ card.title }}</div>
              <EBadge :variant="card.badgeVariant" class="shrink-0 ml-2">{{ card.badge }}</EBadge>
            </div>
            <p class="text-sm text-muted-foreground leading-relaxed">{{ card.desc }}</p>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Quick Start -->
    <div>
      <h2 class="text-xl font-semibold mb-4">快速开始</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ECard>
          <div class="font-medium mb-2">前端</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-3 overflow-x-auto"><code>pnpm add @danweiyuan/eui @danweiyuan/core</code></pre>
        </ECard>
        <ECard>
          <div class="font-medium mb-2">后端</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-3 overflow-x-auto"><code>uv add danweiyuan-base</code></pre>
        </ECard>
        <ECard>
          <div class="font-medium mb-2">脚手架</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-3 overflow-x-auto"><code>npm i -g create-dwy
dwy create my-app</code></pre>
        </ECard>
        <ECard>
          <div class="font-medium mb-2">Claude 配置同步</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-3 overflow-x-auto"><code>dwy sync claude
dwy sync project-claude</code></pre>
        </ECard>
      </div>
    </div>
  </div>
</template>
