<script setup lang="ts">
const skills = [
  { name: 'dwy-frontend-eui', title: '@danweiyuan/eui', desc: 'Vue 3 组件库速查 — 89 组件完整 API', path: '/claude/skills/dwy-frontend-eui' },
  { name: 'dwy-frontend-ekit', title: '@danweiyuan/ekit', desc: '前端工具库速查 — request/storage/validators/date/hooks', path: '/claude/skills/dwy-frontend-ekit' },
  { name: 'dwy-backend-eapi', title: 'danweiyuan-eapi', desc: 'FastAPI 后端基础设施速查 — 8 模块全异步', path: '/claude/skills/dwy-backend-eapi' },
]

const rules = [
  { name: 'server-security', title: '服务器安全', desc: '端口隔离、防火墙、Nginx、Docker、SSH 等部署安全规则', path: '/claude/rules/server-security' },
  { name: 'git-security', title: 'Git 提交安全', desc: '禁止提交敏感文件/内容、.gitignore 规范', path: '/claude/rules/git-security' },
  { name: 'python-code-style', title: 'Python 代码规范', desc: 'FastAPI 项目结构、类型标注、异步编程等 19 章规范', path: '/claude/rules/python-code-style' },
  { name: 'vue-code-style', title: 'Vue 代码规范', desc: 'Composition API、TypeScript、Pinia、路由等 13 章规范', path: '/claude/rules/vue-code-style' },
  { name: 'backend-security', title: '后端安全编码', desc: 'ID 防遍历、密码安全、注入防护、审计日志等 15 章规范', path: '/claude/rules/backend-security' },
]

const hooks = [
  { name: 'pre-git-commit-sensitive-check', title: 'Git 提交敏感检查', desc: '在 git commit 前自动扫描暂存区敏感数据', path: '/claude/hooks/pre-git-commit-sensitive-check' },
]
</script>

<template>
  <div class="max-w-4xl">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Claude Code 配置</h1>
      <p class="text-muted-foreground text-lg">
        通过 create-dwy 管理的 Claude Code 全局配置，包含 Skills、Rules、Hooks 和 Settings。
      </p>
    </div>

    <!-- Skills -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-1">Skills</h2>
      <p class="text-sm text-muted-foreground mb-4">3 个技能 — Claude 在特定场景自动触发的领域知识</p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <router-link
          v-for="skill in skills"
          :key="skill.name"
          :to="skill.path"
        >
          <ECard class="h-full hover:bg-accent transition-colors cursor-pointer">
            <div class="font-medium mb-1">{{ skill.title }}</div>
            <div class="text-sm text-muted-foreground">{{ skill.desc }}</div>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Rules -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-1">Rules</h2>
      <p class="text-sm text-muted-foreground mb-4">5 条规则 — Claude 生成代码时强制遵循的约束</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <router-link
          v-for="rule in rules"
          :key="rule.name"
          :to="rule.path"
        >
          <ECard class="h-full hover:bg-accent transition-colors cursor-pointer">
            <div class="font-medium mb-1">{{ rule.title }}</div>
            <div class="text-sm text-muted-foreground">{{ rule.desc }}</div>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Hooks -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-1">Hooks</h2>
      <p class="text-sm text-muted-foreground mb-4">1 个钩子 — Claude 执行工具前/后的自动化脚本</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <router-link
          v-for="hook in hooks"
          :key="hook.name"
          :to="hook.path"
        >
          <ECard class="h-full hover:bg-accent transition-colors cursor-pointer">
            <div class="font-medium mb-1">{{ hook.title }}</div>
            <div class="text-sm text-muted-foreground">{{ hook.desc }}</div>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Settings -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-1">Settings</h2>
      <p class="text-sm text-muted-foreground mb-4">全局设置 — hooks 配置文件</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <router-link to="/claude/settings">
          <ECard class="h-full hover:bg-accent transition-colors cursor-pointer">
            <div class="font-medium mb-1">settings.json</div>
            <div class="text-sm text-muted-foreground">Claude Code 全局 hooks 和行为配置</div>
          </ECard>
        </router-link>
      </div>
    </div>
  </div>
</template>
