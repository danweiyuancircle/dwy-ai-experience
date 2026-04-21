# @dwydev/eui 集成指南

在你的 Vue 3 项目中集成 @dwydev/eui 组件库。

## 1. 安装依赖

### 安装组件库

```bash
pnpm add @dwydev/eui
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

### 已知问题：vue-sonner 需手动安装

`vue-sonner` 已声明在 EUI 的 `dependencies` 中，但 pnpm 的严格依赖提升策略可能导致它无法被项目正确解析。如果使用 Toast 组件时遇到模块找不到的错误，需手动安装：

```bash
pnpm add vue-sonner
```

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
@import "@dwydev/eui/theme";
```

> 主题 CSS 已内置 `@source` 指令，Tailwind 会自动扫描组件使用的工具类，无需手动配置。

### 可选：按需引入主题

```css
/* 完整主题（推荐） */
@import "@dwydev/eui/theme";

/* 或分别引入 */
@import "@dwydev/eui/theme/tokens";  /* 基础变量 + Tailwind */
@import "@dwydev/eui/theme/dark";    /* 暗色模式 */
```

## 4. 注册组件

### 全局注册（推荐）

```ts
// main.ts
import './style.css'
import { createApp } from 'vue'
import EUI from '@dwydev/eui'
import App from './App.vue'

const app = createApp(App)
app.use(EUI)
app.mount('#app')
```

注册后所有组件全局可用，无需逐个导入。

### 按需导入

```ts
// 在组件中按需导入
import { EButton, EInput, ETable } from '@dwydev/eui'
```

适合对打包体积敏感的场景，支持 Tree-shaking。

## 5. 全局配置 EConfigProvider（必须）

**EConfigProvider 是使用 EUI 的前置条件。** 必须在 App 根组件用 `<EConfigProvider>` 包裹整个应用，否则以下功能不生效：

- **国际化** — 日期选择器、日历等组件将显示英文而非中文
- **全局尺寸** — 无法统一控制所有组件的尺寸
- **弹层层级** — Dialog/Drawer/Popover 等弹层 z-index 无法统一管理
- **UI 文案** — 确定/取消/暂无数据等通用文案无法全局配置

### 基础用法

```vue
<!-- App.vue -->
<script setup lang="ts">
import { EConfigProvider } from '@dwydev/eui'
</script>

<template>
  <EConfigProvider>
    <RouterView />
  </EConfigProvider>
</template>
```

使用默认配置即可满足中文项目需求，无需传任何 props。

### Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| size | `'sm' \| 'default' \| 'lg'` | `'default'` | 所有组件的全局尺寸 |
| zIndex | `number` | `2000` | 弹层组件的基准 z-index |
| locale | `Record<string, string>` | 见下方 | 国际化配置 |

### locale 配置

locale 是一个扁平的键值对象，`name` 字段为 BCP 47 语言标签，控制日期类组件的本地化显示；其余字段为 UI 通用文案。

| 字段 | 默认值 | 说明 |
|------|--------|------|
| name | `'zh-CN'` | BCP 47 语言标签，控制 EDatePicker、ECalendar 等组件的月份名、星期名、年份格式 |
| confirm | `'确定'` | 确认按钮文案 |
| cancel | `'取消'` | 取消按钮文案 |
| close | `'关闭'` | 关闭按钮文案 |
| loading | `'加载中...'` | 加载状态文案 |
| empty | `'暂无数据'` | 空状态文案 |
| search | `'搜索'` | 搜索占位文案 |
| selectPlaceholder | `'请选择'` | 选择器默认占位文案 |
| inputPlaceholder | `'请输入'` | 输入框默认占位文案 |

### 自定义配置示例

```vue
<EConfigProvider
  size="sm"
  :z-index="3000"
  :locale="{
    name: 'en-US',
    confirm: 'OK',
    cancel: 'Cancel',
    close: 'Close',
    loading: 'Loading...',
    empty: 'No data',
    search: 'Search',
    selectPlaceholder: 'Please select',
    inputPlaceholder: 'Please input',
  }"
>
  <RouterView />
</EConfigProvider>
```

### 嵌套覆盖

EConfigProvider 支持嵌套，内层配置覆盖外层，适用于局部区域需要不同配置的场景：

```vue
<EConfigProvider>                                          <!-- 全局中文 -->
  <EConfigProvider :locale="{ name: 'en-US', ... }">      <!-- 局部英文 -->
    <EDatePicker type="month" />                           <!-- 显示英文月份 -->
  </EConfigProvider>
</EConfigProvider>
```

## 6. 主题配置（可选）

### 暗色模式 + 主题切换

```vue
<script setup lang="ts">
import { useTheme } from '@dwydev/eui'

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

## 7. Composables

### useToast

轻量 toast 通知。需要在根组件挂载 `<EToast />` 容器：

```vue
<!-- App.vue -->
<template>
  <router-view />
  <EToast rich-colors />
</template>
```

使用：

```ts
import { useToast } from '@dwydev/eui'

const toast = useToast()

toast.success('操作成功')
toast.error('操作失败')
toast.warning('警告信息')
toast.info('提示信息')

// 带描述
toast.success('保存成功', { description: '数据已持久化' })

// 自定义时长（毫秒）
toast.info('处理中...', { duration: 5000 })
```

### useMessage

```ts
import { useMessage } from '@dwydev/eui'

const message = useMessage()

message.success('操作成功')
message.error('操作失败')
message.warning('警告信息')
message.info('提示信息')
```

### useNotification

```ts
import { useNotification } from '@dwydev/eui'

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
│   ├── style.css          # @import "@dwydev/eui/theme"
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
    "@dwydev/eui": "^1.2.0",
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
