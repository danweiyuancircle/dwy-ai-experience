# EUI 页面设计风格规范

> AI 使用 @dwydev/eui 编写 UI 页面时必须遵循此规范。

## 一、设计风格定位

**shadcn 风格 + 中后台场景**：干净、克制、功能优先。不追求视觉冲击力，追求信息密度和操作效率。

| 维度 | 规范 |
|------|------|
| 风格 | 扁平、无装饰、留白适度 |
| 色彩 | 中性灰为主，主色点缀，不超过 3 种颜色 |
| 圆角 | 统一 `rounded-md`（0.625rem），不混用不同圆角 |
| 阴影 | 仅 `shadow-xs` / `shadow-sm`，不用 `shadow-lg` 及以上 |
| 边框 | 1px `border-border`，不用粗边框 |
| 图标 | 只用 `lucide-vue-next`，不用 emoji、不用其他图标库 |
| 字体 | 系统字体栈（不引入额外字体），依赖 Tailwind 默认 |

## 二、颜色系统

### 语义色（直接使用，不写具体色值）

| 用途 | Tailwind class | 说明 |
|------|---------------|------|
| 页面背景 | `bg-background` | 浅色/深色自动切换 |
| 主文本 | `text-foreground` | 最高对比度 |
| 次要文本 | `text-muted-foreground` | 描述、辅助信息 |
| 主色按钮/强调 | `bg-primary text-primary-foreground` | 主操作 |
| 次要按钮 | `bg-secondary text-secondary-foreground` | 次要操作 |
| 卡片背景 | `bg-card text-card-foreground` | 卡片容器 |
| 危险/错误 | `text-destructive` / `bg-destructive` | 删除、错误 |
| 边框 | `border-border` | 统一边框色 |
| 输入框边框 | `border-input` | 表单控件 |
| 聚焦环 | `ring-ring` | focus 状态 |

### 禁止

- **禁止**写死色值（如 `bg-[#3B82F6]`），必须用语义 token
- **禁止**用 `bg-blue-500` 等 Tailwind 原始色（除了 chart 场景）
- **禁止**超过 3 种颜色混用

### 主题色

EUI 支持 7 种主题色，通过 `<html class="theme-blue">` 切换，代码中不需要关心具体色值：

neutral（默认）| blue | green | rose | orange | violet | slate

## 三、暗色模式

- 所有页面必须同时支持亮色和暗色
- 使用语义色 token 自动适配，不需要手写 `dark:` 前缀
- 特殊场景需要区分时使用 `dark:` 变体
- 背景层级：`bg-background` > `bg-card` > `bg-muted`
- 暗色模式下避免纯白文字，用 `text-foreground` 自动适配

## 四、布局规范

### 页面结构

```vue
<!-- 标准中后台页面 -->
<div class="flex flex-col gap-6 p-6">
  <!-- 页头：标题 + 操作 -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-semibold">页面标题</h1>
      <p class="text-sm text-muted-foreground">页面描述</p>
    </div>
    <div class="flex gap-2">
      <EButton variant="outline">次要操作</EButton>
      <EButton>主操作</EButton>
    </div>
  </div>

  <!-- 内容区 -->
  <div>...</div>
</div>
```

### 间距规则

| 场景 | 间距 | 说明 |
|------|------|------|
| 页面内边距 | `p-6` | 24px |
| 区块间距 | `gap-6` | 24px |
| 卡片内边距 | `p-4` 或 `p-6` | 16px 或 24px |
| 表单项间距 | `space-y-4` | 16px |
| 按钮间距 | `gap-2` | 8px |
| 紧凑元素间距 | `gap-1` | 4px |

### 按钮放置

- 表单/弹窗的操作按钮**右对齐**：`flex justify-end gap-2`
- 次要操作在前（左），主操作在后（右）
- 危险操作用 `variant="destructive"`，放最右

## 五、组件使用规范

### 优先级

使用 EUI 组件的优先级：**EUI 组件 > 组合组件 > 原生 HTML**

| 需求 | 使用 | 不使用 |
|------|------|--------|
| 按钮 | `<EButton>` | `<button>` |
| 输入框 | `<EInput>` | `<input>` |
| 下拉选择 | `<ESelect>` | `<select>` |
| 开关 | `<ESwitch>` | `<input type="checkbox">` |
| 表格 | `<ETable>` | `<table>` |
| 弹窗 | `<EDialog>` | 自定义 modal |
| 轻提示 | `useMessage()` / `toast()` | `alert()` |
| 表单 | `<EForm>` | `<form>` |
| 确认框 | `<EConfirmDialog>` | `confirm()` |

### 表单

> **禁止使用原生 `<form>` 标签。** 所有表单必须使用 `<EForm>` 组件，EForm 内置 vee-validate 校验、provide/inject 上下文传递、统一的 label 布局和 reset/validate API，原生 `<form>` 无法与 EUI 表单体系集成。

```vue
<!-- 标准表单 -->
<EForm ref="formRef" :model="model" :rules="rules" label-width="80px">
  <EFormItem label="名称" prop="name">
    <EInput v-model="model.name" placeholder="请输入" />
  </EFormItem>
  <EFormItem>
    <div class="flex justify-end gap-2">
      <EButton variant="outline" @click="handleReset">重置</EButton>
      <EButton @click="handleSubmit">提交</EButton>
    </div>
  </EFormItem>
</EForm>
```

### 表格页

```vue
<!-- 标准 CRUD 列表页 -->
<div class="flex flex-col gap-6 p-6">
  <!-- 筛选栏 -->
  <EForm inline :model="filters">
    <EFormItem label="关键词">
      <EInput v-model="filters.keyword" placeholder="搜索..." />
    </EFormItem>
    <EFormItem>
      <EButton @click="search">搜索</EButton>
    </EFormItem>
  </EForm>

  <!-- 表格 -->
  <ETable :data="list" :columns="columns" :loading="loading" />

  <!-- 分页 -->
  <EPagination
    v-model="page"
    :total="total"
    v-model:pageSize="pageSize"
    showSizeChanger
    showTotal
  />
</div>
```

### 弹窗

- 表单弹窗用 `<EFormDialog>` 或 `<EDialog>` + 表单
- 确认操作用 `<EConfirmDialog>`
- Dialog 内容超长时自动滚动（body 区域），header/footer 固定
- `maxWidth` 控制宽度：表单弹窗 `500px`，详情弹窗 `600px`

## 六、排版规范

| 元素 | class | 场景 |
|------|-------|------|
| 页面标题 | `text-2xl font-semibold` | h1 |
| 区块标题 | `text-lg font-semibold` | h2 |
| 卡片标题 | `text-base font-medium` | h3 |
| 正文 | `text-sm` | 默认文本 |
| 辅助文字 | `text-sm text-muted-foreground` | 描述、提示 |
| 小字 | `text-xs text-muted-foreground` | 时间戳、标签 |

### 禁止

- **禁止**超过 `text-3xl` 的字号（中后台不需要）
- **禁止**用 `font-bold`（用 `font-semibold` 或 `font-medium`）
- **禁止**正文用 `text-xs`（太小）

## 七、交互规范

### 状态反馈

| 操作 | 反馈方式 |
|------|---------|
| 表单提交成功 | `toast.success('保存成功')` 或 `useMessage().success()` |
| 表单提交失败 | 字段级错误提示（EForm 自动处理） |
| 删除确认 | `<EConfirmDialog type="warning">` |
| 异步加载 | `<ETable :loading="true">` 或 `<ESkeleton>` |
| 空数据 | `<EEmpty>` |

### 过渡动画

- 弹窗/抽屉：EUI 组件内置，不需要额外处理
- 列表切换：`<Transition>` + `duration-200`
- 加载态：`<ESkeleton>` 占位，不用空白闪烁
- **禁止**花哨动画（弹跳、旋转入场等）

### 响应式

| 断点 | 宽度 | 场景 |
|------|------|------|
| sm | 640px | 手机横屏 |
| md | 768px | 平板 |
| lg | 1024px | 小桌面 |
| xl | 1280px | 标准桌面 |

中后台页面最小支持 `md`（768px），不强求手机适配。

## 八、ESelect 特殊约束

- `option.value` **不能为空字符串**（reka-ui 不支持）
- 需要"全部"选项时 value 用 `'all'`，不用 `''`

## 九、卡片/面板规范

```vue
<!-- 标准卡片 -->
<div class="rounded-lg border bg-card p-6">
  <h3 class="text-base font-medium mb-4">卡片标题</h3>
  <!-- 内容 -->
</div>

<!-- 统计卡片 -->
<div class="rounded-lg border bg-card p-4">
  <p class="text-sm text-muted-foreground">指标名称</p>
  <p class="text-2xl font-semibold mt-1">1,234</p>
</div>
```

- 卡片用 `rounded-lg border bg-card`，不加阴影
- 卡片标题和内容间距 `mb-4`
- 统计卡片用紧凑内边距 `p-4`

## 十、代码自检清单

AI 生成页面代码后，逐条验证：

| # | 检查项 |
|---|--------|
| 1 | 颜色只用语义 token（bg-primary/text-foreground 等），不写死色值 |
| 2 | 图标只用 lucide-vue-next，无 emoji |
| 3 | 表单必须用 EForm，表单控件用 EUI 组件，禁止原生 `<form>` 和原生 HTML 控件 |
| 4 | 按钮操作区右对齐，次要在前主要在后 |
| 5 | 弹窗指定 maxWidth，不让内容无限撑开 |
| 6 | 可交互元素有 hover 反馈和 cursor-pointer |
| 7 | 文本层级清晰：标题 semibold、正文 sm、辅助 muted-foreground |
| 8 | 暗色模式下所有元素可见可读 |
| 9 | 空状态用 EEmpty，加载态用 loading prop 或 ESkeleton |
| 10 | ESelect 选项 value 不为空字符串 |
