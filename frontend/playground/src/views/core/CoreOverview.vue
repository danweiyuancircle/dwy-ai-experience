<script setup lang="ts">
const modules = [
  {
    name: 'Request',
    path: '/core/request',
    desc: 'Axios 插件化封装，内置 token 注入、响应解包、自动刷新 token 等插件',
    icon: 'globe',
  },
  {
    name: 'Storage',
    path: '/core/storage',
    desc: 'localStorage 响应式封装，支持 Vue Ref 自动同步和静态工具方法',
    icon: 'database',
  },
  {
    name: 'Validators',
    path: '/core/validators',
    desc: '常用校验函数：手机号、邮箱、身份证、URL、必填、长度校验',
    icon: 'shield-check',
  },
  {
    name: 'Date',
    path: '/core/date',
    desc: '日期格式化工具：日期、日期时间、时间、中文相对时间',
    icon: 'calendar',
  },
  {
    name: 'Hooks',
    path: '/core/hooks',
    desc: 'Vue Composables：useDebounce、useClickOutside、useEventListener',
    icon: 'zap',
  },
]
</script>

<template>
  <div class="max-w-4xl">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">@dwydev/ekit</h1>
      <p class="text-muted-foreground text-lg">
        Vue 3 项目通用工具库，包含 5 个模块：request、storage、validators、date、hooks。
      </p>
    </div>

    <!-- Install -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">安装</h2>
      <div class="border rounded-lg p-4 bg-muted/50">
        <code class="text-sm">pnpm add @dwydev/ekit</code>
        <p class="text-xs text-muted-foreground mt-2">peerDependencies: axios ^1.0.0, vue ^3.4.0</p>
      </div>
    </div>

    <!-- Import -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">按需导入</h2>
      <div class="border rounded-lg p-4 bg-muted/50">
        <pre class="text-sm leading-relaxed"><code>import { createRequest, useStorage, isPhone, formatDate, useDebounce } from '@dwydev/ekit'</code></pre>
      </div>
    </div>

    <!-- Module Cards -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">模块</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <router-link
          v-for="mod in modules"
          :key="mod.path"
          :to="mod.path"
          class="block"
        >
          <ECard class="h-full hover:border-primary/50 transition-colors cursor-pointer">
            <template #header>
              <div class="font-semibold text-base">{{ mod.name }}</div>
            </template>
            <p class="text-sm text-muted-foreground">{{ mod.desc }}</p>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Source -->
    <div>
      <h2 class="text-xl font-semibold mb-4">源码</h2>
      <p class="text-sm text-muted-foreground">
        每个模块源码在 <code class="text-xs px-1.5 py-0.5 rounded bg-muted">frontend/ekit/src/{module}/index.ts</code>，函数简短可直接阅读。
      </p>
    </div>
  </div>
</template>
