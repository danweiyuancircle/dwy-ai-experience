# EUI 落地页设计风格规范

> AI 使用 @danweiyuan/eui 编写落地页时必须遵循此规范。
> 本规范与 `eui-design-guide.md`（中后台规范）互补，落地页特有规则在此定义，通用规则（颜色系统、暗色模式、ESelect 约束等）仍遵循中后台规范。

## 一、落地页 vs 中后台的核心差异

| 维度 | 中后台 | 落地页 |
|------|--------|--------|
| 目标 | 操作效率、信息密度 | 转化率、品牌传达 |
| 字号 | `text-sm` ~ `text-2xl` | `text-base` ~ `text-6xl` |
| 留白 | 紧凑 `p-6 gap-6` | 大量 `py-16 lg:py-24` |
| 宽度 | 满屏利用 | `max-w-6xl mx-auto` 居中 |
| 响应式 | 最小 `md`（768px） | 最小 `sm`（375px），手机优先 |
| 阴影 | `shadow-xs` / `shadow-sm` | 可用 `shadow-md` / `shadow-lg` |
| 动画 | 几乎不用 | 适度滚动入场动画 |

## 二、页面结构模板

### 通用 Section 结构

落地页由多个全宽 Section 垂直堆叠，每个 Section 内部居中限宽：

```vue
<section class="py-16 lg:py-24">
  <div class="max-w-6xl mx-auto px-6">
    <!-- Section 内容 -->
  </div>
</section>
```

### 标准 Section 顺序

| 序号 | Section | 目的 | 必须 |
|------|---------|------|------|
| 1 | Hero | 核心价值主张 + 主 CTA | 是 |
| 2 | 社会证明 | 客户 Logo 墙 / 数字指标 | 推荐 |
| 3 | 功能/特性 | 3-4 个核心卖点 | 是 |
| 4 | 产品展示 | 截图 / 动图 / 视频 | 推荐 |
| 5 | 用户评价 | 真实用户推荐语 | 推荐 |
| 6 | 定价方案 | 2-3 档价格卡片 | 可选 |
| 7 | FAQ | 常见疑虑解答 | 推荐 |
| 8 | 底部 CTA | 再次强调行动号召 | 是 |
| 9 | Footer | 链接 / 版权 / 备案 | 是 |

可根据产品类型增减，但 **Hero + 功能 + 底部 CTA + Footer** 是最小集。

## 三、导航栏

```vue
<header class="fixed top-0 inset-x-0 z-50 border-b bg-background/80 backdrop-blur-sm">
  <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
    <!-- Logo -->
    <a href="/" class="text-lg font-semibold">Brand</a>

    <!-- 导航链接（桌面端） -->
    <nav class="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
      <a href="#features" class="hover:text-foreground transition-colors">功能</a>
      <a href="#pricing" class="hover:text-foreground transition-colors">定价</a>
      <a href="#faq" class="hover:text-foreground transition-colors">FAQ</a>
    </nav>

    <!-- CTA -->
    <div class="flex items-center gap-2">
      <EButton variant="ghost" size="sm">登录</EButton>
      <EButton size="sm">免费试用</EButton>
    </div>
  </div>
</header>
```

规则：
- `fixed` 定位 + `backdrop-blur-sm` 毛玻璃效果
- `bg-background/80` 半透明，不用纯色遮挡
- 内容区 `max-w-6xl mx-auto px-6` 与 Section 对齐
- 移动端隐藏导航链接（`hidden md:flex`），用汉堡菜单或只保留 CTA
- 页面 `scroll-behavior: smooth` 锚点平滑滚动

## 四、Hero Section

```vue
<section class="pt-32 pb-16 lg:pb-24">
  <div class="max-w-6xl mx-auto px-6 text-center">
    <!-- 标签 -->
    <EBadge variant="secondary" class="mb-4">全新发布 v2.0</EBadge>

    <!-- 主标题 -->
    <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
      一句话说清<span class="text-primary">核心价值</span>
    </h1>

    <!-- 副标题 -->
    <p class="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
      用一两句话补充说明，解决什么问题，给谁用。
    </p>

    <!-- CTA 按钮组 -->
    <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
      <EButton size="lg">免费开始</EButton>
      <EButton variant="outline" size="lg">查看演示</EButton>
    </div>

    <!-- 产品截图 -->
    <div class="mt-16 rounded-xl border shadow-lg overflow-hidden">
      <img src="/hero-screenshot.png" alt="产品截图" class="w-full" />
    </div>
  </div>
</section>
```

规则：
- `pt-32` 给固定导航栏留空间
- 标题 `text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight`
- 关键词用 `text-primary` 高亮，不超过一处
- 副标题 `max-w-2xl mx-auto` 控制行宽（65-75 字符）
- CTA 按钮用 `size="lg"`，主次分明
- 移动端 CTA 纵向排列（`flex-col sm:flex-row`）

## 五、功能/特性 Section

### 3 列卡片网格

```vue
<section id="features" class="py-16 lg:py-24">
  <div class="max-w-6xl mx-auto px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-bold">核心功能</h2>
      <p class="mt-3 text-lg text-muted-foreground">一句话描述</p>
    </div>

    <div class="grid md:grid-cols-3 gap-8">
      <div v-for="feature in features" :key="feature.title"
        class="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow"
      >
        <div class="size-10 rounded-md bg-primary/10 flex items-center justify-center mb-4">
          <component :is="feature.icon" class="size-5 text-primary" />
        </div>
        <h3 class="text-lg font-semibold mb-2">{{ feature.title }}</h3>
        <p class="text-sm text-muted-foreground leading-relaxed">{{ feature.description }}</p>
      </div>
    </div>
  </div>
</section>
```

规则：
- 桌面 3 列（`md:grid-cols-3`），移动端单列自动堆叠
- 图标用 `bg-primary/10` 浅色底 + `text-primary` 图标色
- 卡片 hover 用 `hover:shadow-md transition-shadow`，不缩放
- 功能数量 3、4、6 个，保持网格整齐

### 左右交替布局

```vue
<div class="grid md:grid-cols-2 gap-12 items-center">
  <div :class="index % 2 === 1 && 'md:order-2'">
    <img :src="feature.image" :alt="feature.title" class="rounded-lg border" />
  </div>
  <div>
    <h3 class="text-2xl font-bold mb-4">{{ feature.title }}</h3>
    <p class="text-muted-foreground leading-relaxed">{{ feature.description }}</p>
  </div>
</div>
```

适合有产品截图的场景，左图右文 / 右图左文交替。

## 六、社会证明

### Logo 墙

```vue
<section class="py-12 border-y bg-muted/30">
  <div class="max-w-6xl mx-auto px-6">
    <p class="text-center text-sm text-muted-foreground mb-8">
      受到以下企业信赖
    </p>
    <div class="flex flex-wrap items-center justify-center gap-x-12 gap-y-6 opacity-60">
      <!-- SVG Logos，不用 emoji -->
    </div>
  </div>
</section>
```

### 数字指标

```vue
<div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
  <div v-for="stat in stats" :key="stat.label">
    <p class="text-3xl md:text-4xl font-bold text-primary">{{ stat.value }}</p>
    <p class="mt-1 text-sm text-muted-foreground">{{ stat.label }}</p>
  </div>
</div>
```

规则：
- Logo 统一灰度 + 降低透明度（`opacity-60`），不抢主视觉
- 数字指标 2-4 个，数值用 `text-primary font-bold`

## 七、用户评价

```vue
<section class="py-16 lg:py-24 bg-muted/30">
  <div class="max-w-6xl mx-auto px-6">
    <h2 class="text-3xl font-bold text-center mb-12">用户怎么说</h2>

    <div class="grid md:grid-cols-3 gap-6">
      <div v-for="t in testimonials" :key="t.name"
        class="rounded-lg border bg-card p-6"
      >
        <p class="text-sm leading-relaxed mb-4">"{{ t.content }}"</p>
        <div class="flex items-center gap-3">
          <EAvatar :src="t.avatar" :alt="t.name" size="sm" />
          <div>
            <p class="text-sm font-medium">{{ t.name }}</p>
            <p class="text-xs text-muted-foreground">{{ t.title }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

规则：
- 3-5 条评价，有头像 + 姓名 + 职位
- 评价区背景用 `bg-muted/30` 区分层级
- 引号用中文引号，不用 `""`

## 八、定价 Section

```vue
<section id="pricing" class="py-16 lg:py-24">
  <div class="max-w-5xl mx-auto px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-bold">简单透明的定价</h2>
      <p class="mt-3 text-lg text-muted-foreground">选择适合你的方案</p>
    </div>

    <div class="grid md:grid-cols-3 gap-6">
      <div v-for="plan in plans" :key="plan.name"
        :class="[
          'rounded-xl border p-8 flex flex-col',
          plan.popular ? 'border-primary shadow-lg relative' : '',
        ]"
      >
        <EBadge v-if="plan.popular" class="absolute -top-3 left-1/2 -translate-x-1/2">
          最受欢迎
        </EBadge>
        <h3 class="text-lg font-semibold">{{ plan.name }}</h3>
        <p class="text-sm text-muted-foreground mt-1">{{ plan.description }}</p>
        <div class="mt-6">
          <span class="text-4xl font-bold">{{ plan.price }}</span>
          <span class="text-muted-foreground"> /月</span>
        </div>
        <ul class="mt-6 space-y-3 flex-1">
          <li v-for="f in plan.features" :key="f" class="flex items-center gap-2 text-sm">
            <Check class="size-4 text-primary shrink-0" />
            {{ f }}
          </li>
        </ul>
        <EButton
          :variant="plan.popular ? 'default' : 'outline'"
          class="mt-8 w-full"
        >
          {{ plan.cta }}
        </EButton>
      </div>
    </div>
  </div>
</section>
```

规则：
- 2-3 档，推荐档用 `border-primary shadow-lg` 高亮
- "最受欢迎"用 `EBadge` 浮在卡片顶部
- 价格 `text-4xl font-bold`，单位 `text-muted-foreground`
- 功能列表用 Check 图标 + `text-primary`
- 推荐档 CTA 用 `default` variant，其他用 `outline`

## 九、FAQ Section

```vue
<section id="faq" class="py-16 lg:py-24">
  <div class="max-w-3xl mx-auto px-6">
    <h2 class="text-3xl font-bold text-center mb-12">常见问题</h2>
    <EAccordion type="single" collapsible :items="faqItems" />
  </div>
</section>
```

规则：
- 内容区 `max-w-3xl`（比其他 Section 窄，阅读舒适）
- 用 EUI 的 `<EAccordion>` 组件
- 5-8 个问题

## 十、底部 CTA

```vue
<section class="py-16 lg:py-24 bg-primary text-primary-foreground">
  <div class="max-w-4xl mx-auto px-6 text-center">
    <h2 class="text-3xl md:text-4xl font-bold">准备好开始了吗？</h2>
    <p class="mt-4 text-lg opacity-90">一句话再次强调价值</p>
    <div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
      <EButton size="lg" variant="secondary">免费开始</EButton>
      <EButton size="lg" variant="outline" class="border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10">
        联系销售
      </EButton>
    </div>
  </div>
</section>
```

规则：
- 用 `bg-primary text-primary-foreground` 全宽色块，视觉突出
- 主 CTA 用 `variant="secondary"` 反色
- 和 Hero 的 CTA 保持一致的文案

## 十一、Footer

```vue
<footer class="border-t py-12">
  <div class="max-w-6xl mx-auto px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      <div>
        <h4 class="font-semibold mb-4">产品</h4>
        <ul class="space-y-2 text-sm text-muted-foreground">
          <li><a href="#" class="hover:text-foreground transition-colors">功能</a></li>
          <li><a href="#" class="hover:text-foreground transition-colors">定价</a></li>
        </ul>
      </div>
      <!-- 更多列 -->
    </div>
    <div class="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
      &copy; {{ new Date().getFullYear() }} Brand. All rights reserved.
    </div>
  </div>
</footer>
```

## 十二、排版规范（落地页专用）

| 元素 | class | 场景 |
|------|-------|------|
| 主标题（Hero） | `text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight` | 仅 Hero |
| Section 标题 | `text-3xl font-bold` | 各 Section h2 |
| 卡片/功能标题 | `text-lg font-semibold` | h3 |
| 副标题/描述 | `text-lg text-muted-foreground` | Section 描述 |
| 正文 | `text-sm` 或 `text-base` | 卡片内容 |
| 辅助文字 | `text-sm text-muted-foreground` | 标签、备注 |

### 与中后台规范的差异

- 允许 `text-4xl` ~ `text-6xl`（仅 Hero 区域）
- 允许 `font-bold`（标题可用，中后台只用 `font-semibold`）
- 允许 `tracking-tight`（大标题紧凑字距）
- 正文可用 `text-base`（16px），比中后台的 `text-sm` 更大

## 十三、动画规范

### 允许的动画

| 类型 | 实现 | 场景 |
|------|------|------|
| 滚动入场 | `opacity-0 translate-y-4` → `opacity-100 translate-y-0` | Section 内容 |
| 数字递增 | JS 计数动画 | 统计指标 |
| 渐显 | `opacity-0` → `opacity-100` | Logo 墙 |
| 悬停阴影 | `hover:shadow-md transition-shadow` | 功能卡片 |

### 滚动入场实现

```vue
<script setup>
import { useIntersectionObserver } from '@vueuse/core'

const target = ref<HTMLElement | null>(null)
const isVisible = ref(false)

useIntersectionObserver(target, ([{ isIntersecting }]) => {
  if (isIntersecting) isVisible.value = true
}, { threshold: 0.1 })
</script>

<template>
  <div
    ref="target"
    :class="[
      'transition-all duration-700 ease-out',
      isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
    ]"
  >
    <slot />
  </div>
</template>
```

### 禁止的动画

- **禁止** parallax 滚动视差（性能差 + 晕动症）
- **禁止** `animate-bounce` 等持续动画（除 loading）
- **禁止** 入场动画 > 700ms
- **禁止** 滚动劫持（scroll-jacking）
- **必须** 检查 `prefers-reduced-motion`，尊重用户设置

## 十四、响应式规范

落地页**必须**支持手机端（375px 起）：

| 断点 | 布局调整 |
|------|---------|
| < 640px | 单列，CTA 纵向排列，导航隐藏 |
| 640px-768px | 单列或 2 列网格 |
| 768px-1024px | 2-3 列网格 |
| > 1024px | 完整布局 |

关键规则：
- 图片 `w-full rounded-lg`，不固定宽度
- 文字容器 `max-w-2xl mx-auto`，防止超长行
- Grid 用 `grid md:grid-cols-3`，移动端自动单列
- CTA 按钮 `flex-col sm:flex-row`，移动端纵向

## 十五、代码自检清单（落地页专用）

| # | 检查项 |
|---|--------|
| 1 | 颜色只用语义 token，不写死色值 |
| 2 | Hero 标题用 `tracking-tight`，不超过 `text-6xl` |
| 3 | 每个 Section 有 `py-16 lg:py-24` 上下间距 |
| 4 | 内容区 `max-w-6xl mx-auto px-6` 居中限宽 |
| 5 | 图标只用 lucide-vue-next，无 emoji |
| 6 | 导航栏 `fixed` + `backdrop-blur-sm` + `bg-background/80` |
| 7 | Hero 下方 `pt-32` 避免被导航栏遮挡 |
| 8 | CTA 按钮 `size="lg"`，主次分明 |
| 9 | 375px 手机端无水平滚动，布局正常 |
| 10 | 动画 `duration-700` 以内，检查 `prefers-reduced-motion` |
| 11 | 定价卡片推荐档 `border-primary shadow-lg` 高亮 |
| 12 | 暗色模式所有元素可见可读 |
