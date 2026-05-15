---
name: dwy-eui
description: "@dwydev/eui Vue 3 组件库使用指南。当用户在使用 Vue 3 构建页面、选择 UI 组件、查询组件 API、写表单/表格/弹层/导航、配置主题或国际化、使用中后台或落地页设计规范时，**必须**使用此 skill。即使用户没有明确说 'eui'，只要涉及 Vue 3 组件选型、页面布局、表单设计、数据展示、弹层交互、主题切换，也应触发。"
eui_baseline_version: "2.1.0"
---

# @dwydev/eui 组件库使用指南

Vue 3 组件库：Reka-ui 原语层 + shadcn-vue 设计风格 + Element Plus 式 API + Tailwind CSS 4。

本 skill 的索引信息基于 EUI **2.1.0**。消费方项目实际版本可能不同 — 见 [版本兼容规则](#版本兼容规则)。

---

## 集成与设计规范

| 场景 | 读取文件 |
|------|---------|
| 新项目集成 EUI | `references/eui-integration-guide.md` |
| 中后台页面设计规范 | `references/eui-design-guide.md` |
| 落地页/营销页设计规范 | `references/eui-landing-design-guide.md` |

---

## 查 API 标准动作（核心：每次用组件前都做）

EUI 有 87 个组件目录、117 个对外组件。**本文档不再镜像 props/emits 列表** —— 因为它们会随版本漂移。AI 想用某个组件时，按下面顺序拿到精确 API：

### 第一步：定位 EUI 真实版本

读消费方项目的 `package.json`，找 `dependencies["@dwydev/eui"]` 或 `peerDependencies["@dwydev/eui"]`。这个版本号才是 AI 写代码的依据，不是 skill frontmatter 里的 baseline。

### 第二步：读 component-manifest.json（一次拿组件地图）

从 EUI 2.1.0 起，npm 包带一份组件清单：

```
<project-root>/node_modules/@dwydev/eui/dist/component-manifest.json
```

结构（精简示例）：
```json
{
  "version": "2.1.0",
  "componentToDir": { "EButton": "button", "ECommandInput": "command" },
  "directories": {
    "button":  { "types": "components/button/types.d.ts",  "components": ["EButton"] },
    "command": { "types": null, "components": ["ECommand", "ECommandInput", "..."] }
  },
  "composables": ["useMessage", "useTheme", "..."]
}
```

用法：
- 知道组件名（如 `EButton`） → 查 `componentToDir["EButton"]` 拿到目录 `"button"`
- 查 `directories["button"].types` 拿到类型文件相对路径
- 拼接：`<project-root>/node_modules/@dwydev/eui/dist/{types}` 就是要读的 .d.ts

manifest 不存在的回退：
- 消费方装的是 EUI < 2.1.0（旧版本没有 manifest） → 直接走第三步用约定路径
- 仓库无 node_modules（裸 monorepo / 未 install） → 走第三步的 dwy-shared 路径

### 第三步：读组件 types.d.ts（精确 props + emits）

按存在性回退：

```
a. 优先：<project-root>/node_modules/@dwydev/eui/dist/components/{kebab}/types.d.ts
   —— 下游消费方默认场景，含完整 props + emits + JSDoc 注释

b. 次选：<dwy-shared-root>/frontend/eui/src/components/{kebab}/types.ts
   —— 仅当在 dwy-shared monorepo 内或并列 clone 时可用，等价信息

c. 都拿不到 → 退到本文档下方的 [组件目录索引](#组件目录索引)（粗略，仅做导航）
```

`{kebab}` 是目录名规则：组件名去 `E` 前缀后转 kebab-case。
- `EButton` → `button`
- `EDatePicker` → `date-picker`
- `EAdminLayout` → `admin-layout`
- `EAIChat` → `ai-chat`（连续大写视为整体）

**不确定目录名时**：`ls node_modules/@dwydev/eui/dist/components/` 或 `ls frontend/eui/src/components/`，**不要靠猜**。

### 第四步：slots 看 .vue 模板（不在 .d.ts 里）

vue-tsc 输出的 `.d.ts` 中，slots 类型大多被擦平成 `any`。需要 slot 用法（默认插槽、具名插槽、作用域插槽）时，读源码 `.vue` 文件，搜索 `<slot` 看模板里实际定义。

- node_modules 路径下 `.vue` 文件**不存在**（只有 .d.ts），slots 必须回 dwy-shared 源码看
- 拿不到源码时：参考 reka-ui / shadcn-vue 的同名组件 slots 规范，多数 EUI 组件直接转发

### 第五步：冲突时永远信 node_modules

当本 SKILL.md 的描述与消费方项目的 node_modules `.d.ts` 不一致：**无条件以 node_modules 为准**。本文档是导航与心智模型，不是 API 真相。

---

## 版本兼容规则

- 本 skill `eui_baseline_version: 2.1.0`，组件索引、composables 列表、踩坑提示都基于这个版本
- 消费方项目用的是不同版本时（无论更新或更旧），**必须按"查 API 标准动作"流程读 .d.ts**，不要默认本文档准确
- EUI < 2.1.0 没有 `component-manifest.json`：直接走第三步的 types.d.ts 约定路径
- 主版本号变更（1.x → 2.x、2.x → 3.x）时，本文档的索引可能完全失效：必须先 `ls node_modules/@dwydev/eui/dist/components/` 重建认知

---

## 命名约定

- 组件前缀 `E`：`EButton`、`EInput`、`EDialog`
- Props 类型：`E{Name}Props`（如 `EButtonProps`）
- Events 类型：`E{Name}Emits`（如 `EInputEmits`）
- CVA 变体：`{name}Variants`（如 `buttonVariants`）
- 样式合并工具：`cn()` = clsx + tailwind-merge
- 尺寸统一类型：`Size = 'sm' | 'default' | 'lg'`
- 复合组件用 `provide/inject` 共享状态，子组件目录与主组件同处（如 `command/` 下含 ECommand、ECommandInput、ECommandList...）

---

## 重要约束与已知陷阱

源码读不出来的"踩坑经验"，每次写 EUI 代码都遵守：

### 表单
- **禁止用原生 `<form>` 标签**，所有表单必须用 `<EForm>`。EForm 内置 vee-validate 校验、provide/inject 上下文、统一 label 布局和 reset/validate API，原生 `<form>` 无法集成
- `ESelect` 的 `option.value` **不能为空字符串**，reka-ui 不支持
- 表单校验优先用 zod schema 传给 `EForm` 的 `rules` prop

### 弹层
- `EDialog` body 区域有 `overflow-y-auto`，**首尾位置的 input/select 等表单控件的 focus-ring 会被裁切**。规避：在内容区域加 `p-1` 或 `py-1` padding
- 弹层组件统一用 `v-model:open` 控制显隐，不要用 `:visible` / `@update:visible`

### reka-ui 绑定约定
- 封装 reka-ui 组件时统一用 `v-model`（`modelValue` / `update:modelValue`），**不是** `:checked` / `@update:checked`
- 自己写组件包 reka-ui 原语时必须用 `v-model` 或 writable computed 绑定

### 全局配置
- `EConfigProvider` 必须包裹 App 根组件，提供国际化（locale）/ 默认尺寸 / zIndex
- `locale.name` 字段必须是 BCP 47 语言标签（如 `zh-CN`、`en-US`），默认 `zh-CN`

### 样式
- 使用 `cn()` 合并 Tailwind 类名（解决冲突）：`cn('px-2 py-1', isActive && 'bg-primary text-white', className)`
- 主题切换通过 `useTheme()` 的 `setColorTheme()` / `toggleDark()`，**不要**手动操作 `<html class="dark">`

---

## Composables 速查

| Composable | 用途 |
|------------|------|
| `useMessage()` | 全局消息提示（success / warning / error / info） |
| `useNotification()` | 通知（含 title / message / position / duration） |
| `useMessageBox()` | 对话确认（alert / confirm / prompt），返回 Promise |
| `useTheme()` | 主题管理（isDark / setTheme / setColorTheme / toggleDark） |
| `useConfigProvider()` | 读取全局配置（size / zIndex / locale） |
| `useFormField()` | 表单字段上下文（id / name / valid / error），需在 FormField 内使用 |
| `useSecureValue()` | 敏感输入安全绑定（DOM property 赋值，避免密码泄露到 HTML attribute） |

精确签名读 `<project-root>/node_modules/@dwydev/eui/dist/composables/{name}.d.ts`。

---

## 主题系统

- **Design Tokens**：CSS 自定义属性，定义在 `tokens.css`，前缀 `--`（如 `--primary`、`--background`）
- **暗色模式**：`dark.css`，通过 `<html class="dark">` 切换（用 `useTheme().toggleDark()`，不手写）
- **色彩主题**：7 种（neutral / blue / green / rose / orange / violet / slate），通过 `useTheme().setColorTheme()` 切换
- 样式入口：`import '@dwydev/eui/theme'`

---

## 通用类型速查

精确定义读 `<project-root>/node_modules/@dwydev/eui/dist/types.d.ts`。常用：

```ts
type Size = 'sm' | 'default' | 'lg'

interface Option {
  label: string
  value: string | number  // ⚠️ 不能为空字符串
  disabled?: boolean
}

interface MenuItem {
  key: string
  label: string
  icon?: string
  path?: string           // router 模式下的路由路径
  children?: MenuItem[]
  disabled?: boolean
}

interface TableColumn<T = any> {
  key: string
  title: string
  width?: number | string
  minWidth?: number
  sortable?: boolean
  fixed?: 'left' | 'right'
  align?: 'left' | 'center' | 'right'
  render?: (row: T, index: number) => any
}
```

---

## 组件目录索引

按用途分类的导航表，**只提供组件名 + 一句话用途**，精确 props/emits 一律按 [查 API 标准动作](#查-api-标准动作核心每次用组件前都做) 读 `types.d.ts`。

### 基础展示

| 组件 | 用途 |
|------|------|
| `EButton` | 按钮（含 loading 状态） |
| `EButtonGroup` | 按钮组 |
| `EBadge` | 标签徽章 |
| `EAlert` | 警告提示 |
| `ECard` | 卡片容器 |
| `ELabel` | 标签文本 |
| `ESeparator` | 分隔线 |
| `ETypography` | 排版文本 |
| `EKbd` | 键盘按键展示 |
| `ESpinner` | 加载动画 |
| `EProgress` | 进度条 |
| `ESkeleton` | 骨架屏 |
| `EEmpty` | 空状态 |
| `EAvatar` | 头像 |
| `EImage` | 图片（含懒加载/预览） |
| `EAspectRatio` | 宽高比容器 |
| `EAffix` | 固钉 |
| `EWatermark` | 水印 |

### 表单输入

| 组件 | 用途 |
|------|------|
| `EForm` / `EFormItem` | 表单容器与表单项（必用，禁用原生 form） |
| `EField` | 字段布局（垂直/水平/响应式） |
| `EInput` | 输入框（含 password / clearable / 字数统计） |
| `EInputGroup` | 输入组（含 prefix/suffix addon） |
| `ETextarea` | 多行输入（含自适应高度） |
| `ENumberField` | 数字输入 |
| `ESelect` | 下拉选择（option.value ≠ ''） |
| `ENativeSelect` | 原生 select |
| `ECombobox` | 组合框（可输入下拉） |
| `EAutocomplete` | 自动补全 |
| `ECheckbox` | 复选框/复选组 |
| `ERadio` | 单选组 |
| `ESwitch` | 开关 |
| `ETagsInput` | 标签输入 |
| `EDatePicker` | 日期/范围/月/年选择 |
| `ETimePicker` | 时间选择 |
| `EColorPicker` | 颜色选择 |
| `ERate` | 评分 |
| `ESlider` | 滑块 |
| `ECascader` | 级联选择 |
| `ETreeSelect` | 树选择 |
| `EMention` | @提及输入 |
| `EInputOTP` | OTP 验证码 |
| `EPinInput` | PIN 输入 |
| `EUpload` | 文件上传（含拖拽/图片墙） |
| `ETransfer` | 穿梭框 |

### 数据展示

| 组件 | 用途 |
|------|------|
| `ETable` | 表格（含排序/选择/展开/虚拟滚动/列固定） |
| `EVirtualTable` | 虚拟滚动表格（大数据专用） |
| `EDescriptions` | 描述列表 |
| `ETimeline` | 时间线 |
| `EStatistic` | 统计数值 |
| `ETree` | 树形控件 |
| `ECalendar` | 日历 |
| `ERangeCalendar` | 日期范围日历 |
| `EPagination` | 分页 |
| `EBreadcrumb` | 面包屑 |
| `EChartContainer` | 图表容器 |

### 弹层与反馈

| 组件 | 用途 |
|------|------|
| `EDialog` | 对话框（v-model:open，body 区域 padding 见踩坑提示） |
| `EDrawer` | 抽屉 |
| `ESheet` | 侧边面板 |
| `EAlertDialog` | 确认对话框 |
| `ETooltip` | 提示气泡 |
| `EPopover` | 弹出卡片 |
| `EHoverCard` | 悬停卡片 |
| `EToast` | 轻提示（配合 useToast / `toast()`） |
| `EContextMenu` | 右键菜单 |

### 导航与布局

| 组件 | 用途 |
|------|------|
| `ETabs` | 标签页 |
| `EMenu` | 侧边菜单 |
| `EDropdown` | 下拉菜单 |
| `EAccordion` | 手风琴 |
| `ECollapsible` | 折叠面板 |
| `EStepper` | 步骤条 |
| `ECarousel` | 轮播 |
| `EScrollArea` | 自定义滚动区 |
| `EInfiniteScroll` | 无限滚动 |
| `EToggle` / `EToggleGroup` | 切换按钮 |
| `EItem` | 列表项 |
| `EResizablePanelGroup` 等 | 可调整大小面板（复合组件） |

### 复合组件（子组件需配合使用）

| 主组件 | 用途 |
|--------|------|
| `ECommand` | 命令面板（含 ECommandInput / List / Empty / Group / Item / Separator / Shortcut） |
| `ENavigationMenu` | 导航菜单（含 List / Item / Trigger / Content / Link / Viewport） |
| `EMenubar` | 菜单栏（含 Menu / Trigger / Content / Item / Separator / Checkbox / Radio / Sub） |
| `EResizable` | 可调整大小（含 PanelGroup / Panel / Handle） |

复合组件的全部子组件名查 `component-manifest.json` 的 `directories[{kebab}].components`。

### 业务组件

| 组件 | 用途 |
|------|------|
| `EDataPage` | 数据列表页（内置表格 + 分页 + 搜索） |
| `EFormDialog` | 表单弹窗 |
| `EConfirmDialog` | 确认弹窗（类型: info / warning / error） |
| `EAdminLayout` | 后台管理布局（顶部 + 侧边栏 + 主内容） |
| `EAIChat` | AI 对话 |
| `ETimetableGrid` | 课程表/时间表 |
| `EConfigProvider` | 全局配置（必须包裹 App 根） |
