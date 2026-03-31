<script setup lang="ts">
const commands = [
  {
    name: 'dwy create [name]',
    title: 'create-dwy',
    desc: '交互式项目脚手架，支持 web / mobile / backend 模板，生成完整项目结构',
    path: '/cli/create-dwy',
  },
  {
    name: 'dwy sync claude',
    title: 'sync claude',
    desc: '同步全局 ~/.claude/ 配置（rules、skills、commands、hooks、settings.json）',
    path: '/cli/create-dwy',
  },
  {
    name: 'dwy sync project-claude',
    title: 'sync project-claude',
    desc: '同步项目级 .claude/ 配置，根据 .dwy 标记文件确定模板类型',
    path: '/cli/create-dwy',
  },
]
</script>

<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">create-dwy</h1>
      <p class="text-muted-foreground text-lg">
        项目脚手架 + Claude Code 配置同步 CLI 工具
      </p>
    </div>

    <!-- Install -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">安装</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>npm i -g create-dwy</code></pre>
      </ECard>
    </div>

    <!-- Commands -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">命令一览</h2>
      <div class="grid grid-cols-1 gap-3">
        <router-link
          v-for="cmd in commands"
          :key="cmd.name"
          :to="cmd.path"
          class="block"
        >
          <ECard class="hover:border-primary/50 transition-colors cursor-pointer">
            <div class="flex items-center gap-3 mb-2">
              <code class="text-sm font-mono px-2 py-0.5 rounded bg-muted">{{ cmd.name }}</code>
              <EBadge variant="outline">{{ cmd.title }}</EBadge>
            </div>
            <p class="text-sm text-muted-foreground">{{ cmd.desc }}</p>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Quick Usage -->
    <div>
      <h2 class="text-xl font-semibold mb-4">快速使用</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code># 创建新项目
dwy create my-app

# 同步全局 Claude 配置到 ~/.claude/
dwy sync claude

# 同步项目级 Claude 配置到 .claude/
dwy sync project-claude</code></pre>
      </ECard>
    </div>
  </div>
</template>
