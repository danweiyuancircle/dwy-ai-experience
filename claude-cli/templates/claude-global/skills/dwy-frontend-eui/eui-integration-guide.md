# @danweiyuan/eui 集成指南

在你的 Vue 3 项目中集成 @danweiyuan/eui 组件库。

## 1. 安装依赖

### 安装组件库

```bash
pnpm add @danweiyuan/eui
```

### 安装 Peer Dependencies

```bash
pnpm add -D tailwindcss @tailwindcss/vite tw-animate-css
```

| 包名 | 版本要求 | 说明 |
|------|---------|------|
| `tailwindcss` | `^4.0.0` | CSS 框架 |
| `@tailwindcss/vite` | `^4.0.0` | Vite 插件 |
| `tw-animate-css` | `^1.0.0` | 动画工具类 |

## 2. 配置 Vite

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
```

## 3. 引入样式

```css
/* src/style.css */
@import "@danweiyuan/eui/theme";
```

> 主题 CSS 已内置 `@source` 指令，Tailwind 会自动扫描组件使用的工具类，无需手动配置。

### 可选：按需引入主题

```css
/* 完整主题（推荐） */
@import "@danweiyuan/eui/theme";

/* 或分别引入 */
@import "@danweiyuan/eui/theme/tokens";  /* 基础变量 + Tailwind */
@import "@danweiyuan/eui/theme/dark";    /* 暗色模式 */
```

## 4. 注册组件

### 全局注册（推荐）

```ts
// main.ts
import './style.css'
import { createApp } from 'vue'
import EUI from '@danweiyuan/eui'
import App from './App.vue'

const app = createApp(App)
app.use(EUI)
app.mount('#app')
```

注册后所有组件全局可用，无需逐个导入。

### 按需导入

```ts
// 在组件中按需导入
import { EButton, EInput, ETable } from '@danweiyuan/eui'
```

适合对打包体积敏感的场景，支持 Tree-shaking。

## 5. 主题配置（可选）

### 暗色模式 + 主题切换

```vue
<script setup lang="ts">
import { useTheme } from '@danweiyuan/eui'

const { isDark, toggleDark, colorTheme, setColorTheme } = useTheme()
</script>

<template>
  <EButton @click="toggleDark">
    {{ isDark ? '切换亮色' : '切换暗色' }}
  </EButton>

  <EButton @click="setColorTheme('blue')">
    蓝色主题
  </EButton>
</template>
```

### 内置 7 种颜色主题

| 主题名 | 说明 |
|--------|------|
| `neutral` | 默认主题 |
| `blue` | 蓝色 |
| `green` | 绿色 |
| `rose` | 玫红 |
| `orange` | 橙色 |
| `violet` | 紫色 |
| `slate` | 石板灰 |

## 6. Composables

### useMessage

```ts
import { useMessage } from '@danweiyuan/eui'

const message = useMessage()

message.success('操作成功')
message.error('操作失败')
message.warning('警告信息')
message.info('提示信息')
```

### useNotification

```ts
import { useNotification } from '@danweiyuan/eui'

const notification = useNotification()

notification.success({
  title: '操作成功',
  message: '数据已保存',
})
```

## 完整示例

### 最小项目结构

```
my-app/
├── src/
│   ├── style.css          # @import "@danweiyuan/eui/theme"
│   ├── main.ts            # app.use(EUI)
│   └── App.vue
├── index.html
├── vite.config.ts         # tailwindcss 插件
├── tsconfig.json
└── package.json
```

### package.json 依赖

```json
{
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
}
```
