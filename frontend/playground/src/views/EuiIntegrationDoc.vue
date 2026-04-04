<script setup lang="ts">
const peerDeps = [
  { name: 'tailwindcss', version: '^4.0.0', desc: 'CSS 框架' },
  { name: '@tailwindcss/vite', version: '^4.0.0', desc: 'Vite 插件' },
  { name: 'tw-animate-css', version: '^1.0.0', desc: '动画工具类' },
]

const themes = [
  { name: 'neutral', desc: '默认主题' },
  { name: 'blue', desc: '蓝色' },
  { name: 'green', desc: '绿色' },
  { name: 'rose', desc: '玫红' },
  { name: 'orange', desc: '橙色' },
  { name: 'violet', desc: '紫色' },
  { name: 'slate', desc: '石板灰' },
]
</script>

<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">集成指南</h1>
      <p class="text-muted-foreground text-lg">
        在你的 Vue 3 项目中集成 @danweiyuan/eui
      </p>
    </div>

    <!-- Step 1: Install -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">1. 安装依赖</h2>
      <ECard>
        <div class="font-medium mb-2">安装组件库</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>pnpm add @danweiyuan/eui</code></pre>
      </ECard>
      <ECard class="mt-3">
        <div class="font-medium mb-2">安装 Peer Dependencies</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>pnpm add -D tailwindcss @tailwindcss/vite tw-animate-css</code></pre>
        <div class="mt-3">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b">
                <th class="text-left py-2 font-medium">包名</th>
                <th class="text-left py-2 font-medium">版本要求</th>
                <th class="text-left py-2 font-medium">说明</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dep in peerDeps" :key="dep.name" class="border-b last:border-0">
                <td class="py-2 font-mono text-xs">{{ dep.name }}</td>
                <td class="py-2 text-muted-foreground">{{ dep.version }}</td>
                <td class="py-2 text-muted-foreground">{{ dep.desc }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </ECard>
    </div>

    <!-- Step 2: Vite Config -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">2. 配置 Vite</h2>
      <ECard>
        <div class="font-medium mb-2">vite.config.ts</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})</code></pre>
      </ECard>
    </div>

    <!-- Step 3: CSS -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">3. 引入样式</h2>
      <ECard>
        <div class="font-medium mb-2">src/style.css</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>@import "@danweiyuan/eui/theme";</code></pre>
        <EAlert variant="default" class="mt-3">
          <div class="text-sm">
            主题 CSS 已内置 <code class="font-mono text-xs bg-muted px-1 py-0.5 rounded">@source</code> 指令，Tailwind 会自动扫描组件使用的工具类，无需手动配置。
          </div>
        </EAlert>
      </ECard>
      <ECard class="mt-3">
        <div class="font-medium mb-2">可选：按需引入主题</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>/* 完整主题（推荐） */
@import "@danweiyuan/eui/theme";

/* 或分别引入 */
@import "@danweiyuan/eui/theme/tokens";  /* 基础变量 + Tailwind */
@import "@danweiyuan/eui/theme/dark";    /* 暗色模式 */</code></pre>
      </ECard>
    </div>

    <!-- Step 4: Register -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">4. 注册组件</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <ECard>
          <div class="flex items-center gap-2 mb-2">
            <div class="font-medium">全局注册</div>
            <EBadge variant="default">推荐</EBadge>
          </div>
          <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>// main.ts
import './style.css'
import { createApp } from 'vue'
import EUI from '@danweiyuan/eui'
import App from './App.vue'

const app = createApp(App)
app.use(EUI)
app.mount('#app')</code></pre>
          <p class="text-sm text-muted-foreground mt-2">注册后所有组件全局可用，无需逐个导入。</p>
        </ECard>
        <ECard>
          <div class="font-medium mb-2">按需导入</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>// 在组件中按需导入
import {
  EButton,
  EInput,
  ETable
} from '@danweiyuan/eui'</code></pre>
          <p class="text-sm text-muted-foreground mt-2">适合对打包体积敏感的场景，支持 Tree-shaking。</p>
        </ECard>
      </div>
    </div>

    <!-- Step 5: Theme -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">5. 主题配置（可选）</h2>
      <ECard>
        <div class="font-medium mb-2">暗色模式 + 主题切换</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>&lt;script setup lang="ts"&gt;
import { useTheme } from '@danweiyuan/eui'

const { isDark, toggleDark, colorTheme, setColorTheme } = useTheme()
&lt;/script&gt;

&lt;template&gt;
  &lt;EButton @click="toggleDark"&gt;
    {{ isDark ? '切换亮色' : '切换暗色' }}
  &lt;/EButton&gt;

  &lt;EButton @click="setColorTheme('blue')"&gt;
    蓝色主题
  &lt;/EButton&gt;
&lt;/template&gt;</code></pre>
      </ECard>
      <div class="mt-3">
        <div class="text-sm font-medium mb-2">内置 {{ themes.length }} 种颜色主题</div>
        <div class="flex flex-wrap gap-2">
          <EBadge v-for="t in themes" :key="t.name" variant="outline">
            {{ t.name }} — {{ t.desc }}
          </EBadge>
        </div>
      </div>
    </div>

    <!-- Step 6: Composables -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">6. Composables</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <ECard>
          <div class="font-medium mb-2">useMessage</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>import { useMessage } from '@danweiyuan/eui'

const message = useMessage()

message.success('操作成功')
message.error('操作失败')
message.warning('警告信息')
message.info('提示信息')</code></pre>
        </ECard>
        <ECard>
          <div class="font-medium mb-2">useNotification</div>
          <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>import { useNotification } from '@danweiyuan/eui'

const notification = useNotification()

notification.success({
  title: '操作成功',
  message: '数据已保存',
})</code></pre>
        </ECard>
      </div>
    </div>

    <!-- Full Example -->
    <div class="mb-10">
      <h2 class="text-xl font-semibold mb-4">完整示例</h2>
      <ECard>
        <div class="font-medium mb-2">最小项目结构</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>my-app/
├── src/
│   ├── style.css          # @import "@danweiyuan/eui/theme"
│   ├── main.ts            # app.use(EUI)
│   └── App.vue
├── index.html
├── vite.config.ts         # tailwindcss 插件
├── tsconfig.json
└── package.json</code></pre>
      </ECard>
      <ECard class="mt-3">
        <div class="font-medium mb-2">package.json 依赖</div>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>{
  "dependencies": {
    "@danweiyuan/eui": "^1.2.0",
    "vue": "^3.5.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@vitejs/plugin-vue": "^6.0.0",
    "tailwindcss": "^4.0.0",
    "tw-animate-css": "^1.0.0",
    "vite": "^8.0.0"
  }
}</code></pre>
      </ECard>
    </div>
  </div>
</template>
