---
name: dwy-frontend-eui
description: "@danweiyuan/eui Vue 3 组件库速查。触发条件：使用 Vue 3 构建页面、选择 UI 组件、查询 eui 组件 API 时。"
---

# @danweiyuan/eui 组件速查

基于 Reka-ui 原语层 + shadcn-vue 设计风格 + Element Plus 式 API 的 Vue 3 组件库。

## 集成指南

新项目集成 EUI 时，读取同目录下的 `eui-integration-guide.md`，包含完整的安装、Vite 配置、样式引入、组件注册、主题切换等步骤。

---

## 安装与引入

```bash
pnpm add @danweiyuan/eui
```

```ts
// 按需导入（推荐）
import { EButton, EInput, ETable } from '@danweiyuan/eui'

// 全局注册（Vue plugin）
import EUI from '@danweiyuan/eui'
app.use(EUI)
```

```ts
// 主题 CSS（必须引入）
import '@danweiyuan/eui/theme'          // 基础样式 + tokens
import '@danweiyuan/eui/theme/dark'     // 暗色模式（可选）
import '@danweiyuan/eui/theme/tokens'   // 仅 design tokens（可选）
```

### 全局配置 EConfigProvider（必须）

**EConfigProvider 是使用 EUI 的前置条件。** 必须在 App 根组件用 `<EConfigProvider>` 包裹整个应用，否则以下功能不生效：

- 国际化（日期选择器、月份/年份选择器等显示为英文而非中文）
- 全局组件尺寸统一控制
- 弹层 z-index 统一管理
- 组件内部 UI 文案（确定/取消/暂无数据等）

#### 基础用法

```vue
<!-- App.vue -->
<script setup lang="ts">
import { EConfigProvider } from '@danweiyuan/eui'
</script>

<template>
  <EConfigProvider>
    <RouterView />
  </EConfigProvider>
</template>
```

使用默认配置即可满足中文项目需求，无需传任何 props。

#### Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| size | `'sm' \| 'default' \| 'lg'` | `'default'` | 所有组件的全局尺寸 |
| zIndex | `number` | `2000` | 弹层组件（Dialog/Drawer/Popover 等）的基准 z-index |
| locale | `Record<string, string>` | 见下方 | 国际化配置 |

#### locale 配置

locale 是一个扁平的键值对象，包含两部分内容：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| name | `'zh-CN'` | **BCP 47 语言标签**，控制日期选择器（EDatePicker）、日历（ECalendar）等组件的本地化显示（月份名、星期名、年份格式等） |
| confirm | `'确定'` | 确认按钮文案 |
| cancel | `'取消'` | 取消按钮文案 |
| close | `'关闭'` | 关闭按钮文案 |
| loading | `'加载中...'` | 加载状态文案 |
| empty | `'暂无数据'` | 空状态文案 |
| search | `'搜索'` | 搜索占位文案 |
| selectPlaceholder | `'请选择'` | 选择器默认占位文案 |
| inputPlaceholder | `'请输入'` | 输入框默认占位文案 |

#### 自定义配置示例

```vue
<!-- 英文项目 -->
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

#### 嵌套覆盖

EConfigProvider 支持嵌套，内层配置覆盖外层。适用于局部区域需要不同配置的场景：

```vue
<EConfigProvider>                                          <!-- 全局中文 -->
  <EConfigProvider :locale="{ name: 'en-US', ... }">      <!-- 局部英文 -->
    <EDatePicker type="month" />                           <!-- 显示英文月份 -->
  </EConfigProvider>
</EConfigProvider>
```

#### 实现原理

EConfigProvider 内部做了两件事：
1. 通过 Vue `provide/inject` 向子树注入 size、zIndex、locale 配置，EUI 组件通过 `useConfigProvider()` 读取
2. 包裹 reka-ui 的 `ConfigProvider`，将 `locale.name` 透传为 reka-ui 的全局 locale，所有基于 reka-ui 的日期类组件自动继承

#### 不使用 EConfigProvider 的后果

| 功能 | 不包裹时的表现 |
|------|--------------|
| EDatePicker 月份/星期 | 显示英文（Jan、Feb、Mon、Tue） |
| ECalendar 月份/星期 | 显示英文 |
| 组件尺寸 | 各组件使用各自默认值，无法统一控制 |
| 弹层 z-index | 各组件使用各自默认值，可能层级混乱 |
| UI 文案 | useConfigProvider() 使用内部默认值（中文），但不保证一致性 |

## 命名约定

- 组件前缀 `E`：`EButton`, `EInput`, `EDialog`
- Props 类型：`E{Name}Props`（如 `EButtonProps`）
- Events 类型：`E{Name}Emits`（如 `EInputEmits`）
- CVA 变体：`{name}Variants`（如 `buttonVariants`）
- 样式合并工具：`cn()` = clsx + tailwind-merge
- 尺寸统一类型：`Size = 'sm' | 'default' | 'lg'`

## 查阅完整 API

每个组件的完整 props/slots/events 定义在源码中：

```
frontend/eui/src/components/{component-name}/types.ts
```

需要具体某个组件的详细 API 时，直接读取对应的 `types.ts` 文件。

---

## 组件索引

### 基础组件

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| EButton | 按钮 | variant(default/destructive/outline/secondary/ghost/link), size(default/sm/lg/icon), loading, disabled |
| EBadge | 标签徽章 | variant(default/secondary/destructive/outline) |
| EAlert | 警告提示 | variant(default/destructive), title, description, closable |
| ECard | 卡片容器 | title, description |
| ELabel | 标签文本 | for |
| ESeparator | 分隔线 | orientation(horizontal/vertical) |
| ETypography | 排版文本 | variant, as |
| EKbd | 键盘按键展示 | — |
| ESpinner | 加载动画 | size(sm/default/lg) |
| EProgress | 进度条 | modelValue(0-100) |
| ESkeleton | 骨架屏 | — |
| EEmpty | 空状态 | title, description, icon |
| EAvatar | 头像 | src, alt, fallback, size |
| EImage | 图片 | src, alt, fit, lazy, fallback, preview |

### 表单组件

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| EInput | 输入框 | v-model, type, placeholder, size, clearable, showPassword, disabled, readonly, maxlength, showWordLimit |
| ETextarea | 多行输入 | v-model, placeholder, rows, autoResize, maxlength, disabled, showWordLimit, minRows, maxRows |
| ENumberField | 数字输入 | v-model, min, max, step, size, disabled, precision, controlsPosition, placeholder, readonly |
| ESelect | 下拉选择 | v-model, options(Option[]), placeholder, clearable, size, disabled, filterable, multiple, collapseTags, remote, remoteMethod, loading |
| ENativeSelect | 原生 select | v-model, options(SelectOption[]), placeholder, disabled |
| ECombobox | 组合框 | v-model, options(Option[]), placeholder, emptyText, disabled |
| EAutocomplete | 自动补全 | v-model, fetchSuggestions(async fn), debounce, placeholder |
| ECheckbox | 复选框 | v-model, label, disabled, indeterminate, options(Option[]), direction(horizontal/vertical), border |
| ERadio | 单选组 | v-model, options(Option[]), direction(horizontal/vertical), disabled, optionType(default/button), border, size |
| ESwitch | 开关 | v-model, label, size, disabled |
| ETagsInput | 标签输入 | v-model(string[]), placeholder, max, size, disabled |
| EDatePicker | 日期选择 | v-model, type(date/daterange/month/year), placeholder, startPlaceholder, endPlaceholder, rangeSeparator, format, clearable, disabled, disabledDate, shortcuts(DatePickerShortcut[]) |
| ETimePicker | 时间选择 | v-model, placeholder, format, hourStep, minuteStep, disabled |
| EColorPicker | 颜色选择 | v-model, presets(string[]), showAlpha, disabled |
| ERate | 评分 | v-model, max, allowHalf, showText, disabled |
| ESlider | 滑块 | v-model(number[]), min, max, step, orientation, disabled |
| ECascader | 级联选择 | v-model, options(CascaderOption[]), placeholder, filterable, clearable, lazy, loadFn, multiple, collapseTags |
| ETreeSelect | 树选择 | v-model, data(TreeNode[]), placeholder, multiple, checkable, disabled |
| EMention | @提及输入 | v-model, options(MentionOption[]), prefix, loading, placeholder |
| EInputOTP | OTP 验证码 | v-model, length, disabled, placeholder |
| EPinInput | PIN 输入 | v-model(string[]), length, mask, otp, type(text/number) |
| EUpload | 文件上传 | v-model(UploadFile[]), action, accept, multiple, limit, listType(text/picture/picture-card), drag, beforeUpload, autoUpload, headers, withCredentials |
| ETransfer | 穿梭框 | v-model, data(TransferItem[]), filterable, titles([string, string]) |
| EForm | 表单容器 | model, rules(Zod/FormRule[]), labelWidth, labelPosition(left/right/top), size, disabled, inline |
| EFormItem | 表单项 | （配合 EForm 使用） |
| EField | 字段布局 | orientation(vertical/horizontal/responsive), invalid |
| EInputGroup | 输入组 | 子组件 EInputGroupAddon(align) |

### 数据展示

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| ETable | 表格 | data, columns(TableColumn[]), loading, rowKey, striped, bordered, selectable, selectedKeys, expandable, expandedRowKeys, rowClassName, showSummary, summaryMethod, virtual, virtualRowHeight, resizable |
| EVirtualTable | 虚拟滚动表格 | columns(VirtualTableColumn[]), data, height, estimateRowHeight, rowKey, loading |
| EDescriptions | 描述列表 | items(DescriptionItem[]), columns, bordered, title |
| ETimeline | 时间线 | items(TimelineItem[]), reverse |
| EStatistic | 统计数值 | title, value, prefix, suffix, precision |
| ETree | 树形控件 | data(TreeNode[]), v-model, checkable, expandedKeys, defaultExpandAll, lazy, loadFn, draggable, filterMethod, filterQuery, checkStrictly |
| ECalendar | 日历 | v-model, multiple, disabled, locale, minValue, maxValue |
| ERangeCalendar | 日期范围日历 | v-model({start, end}), disabled, locale, minValue, maxValue |
| EPagination | 分页 | v-model, total, pageSize, showSizeChanger, pageSizes, showTotal, jumper, layout, disabled |
| EBreadcrumb | 面包屑 | items(BreadcrumbItem[]), separator |

### 弹层与反馈

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| EDialog | 对话框 | v-model:open, title, description, showClose, maxWidth, draggable, closeOnClickModal, closeOnPressEscape, fullscreen, destroyOnClose |
| EDrawer | 抽屉 | v-model:open, title, description, direction(top/right/bottom/left), showClose |
| ESheet | 侧边面板 | v-model:open, title, description, side(top/right/bottom/left), showClose |
| EAlertDialog | 确认对话框 | v-model:open, title, description, confirmText, cancelText |
| ETooltip | 提示气泡 | content, side, sideOffset, delayDuration, disabled |
| EPopover | 弹出卡片 | v-model:open, side, sideOffset, align |
| EHoverCard | 悬停卡片 | openDelay, closeDelay |
| EToast | 轻提示 | position, expand, richColors（配合 `toast()` 函数使用） |
| EContextMenu | 右键菜单 | items(ContextMenuItem[]) |

### 导航与布局

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| ETabs | 标签页 | v-model, items(TabItem[]), closable, addable, tabPosition(top/bottom/left/right) |
| EMenu | 侧边菜单 | v-model, items(MenuItem[]), collapsed, router, uniqueOpened, defaultOpeneds |
| EDropdown | 下拉菜单 | items(DropdownMenuItem[]), side, align, sideOffset, trigger(click/hover), splitButton, buttonText, buttonVariant |
| EAccordion | 手风琴 | v-model, items(AccordionItemOption[]), multiple, collapsible |
| ECollapsible | 折叠面板 | v-model(boolean), disabled |
| EStepper | 步骤条 | v-model, items(StepperItem[]), direction(horizontal/vertical) |
| ECarousel | 轮播 | loop, direction, showArrows, showDots, autoplay, interval。子组件 ECarouselItem |
| EScrollArea | 自定义滚动区 | type(auto/always/scroll/hover) |
| EInfiniteScroll | 无限滚动 | loading, disabled, distance |

### 复合组件

以下组件由多个子组件组合使用，通过 `provide/inject` 共享状态：

| 组件 | 子组件 | 用途 |
|------|--------|------|
| ECommand | ECommandInput, ECommandList, ECommandEmpty, ECommandGroup, ECommandItem, ECommandSeparator, ECommandShortcut | 命令面板（配合 useCommand） |
| ENavigationMenu | ENavigationMenuList, ENavigationMenuItem, ENavigationMenuTrigger, ENavigationMenuContent, ENavigationMenuLink, ENavigationMenuViewport | 导航菜单 |
| EMenubar | EMenubarMenu, EMenubarTrigger, EMenubarContent, EMenubarItem, EMenubarSeparator, EMenubarCheckboxItem, EMenubarRadioGroup, EMenubarRadioItem, EMenubarSub, EMenubarSubTrigger, EMenubarSubContent | 菜单栏 |
| EResizable | EResizablePanelGroup(direction), EResizablePanel(defaultSize, minSize, maxSize), EResizableHandle(withHandle) | 可调整大小面板 |

### 其他

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| EConfigProvider | **必须**包裹 App 根组件，提供国际化/尺寸/层级全局配置 | size, zIndex, locale(Record, 含 name 字段为 BCP 47 语言标签，默认 zh-CN) |
| EToggle | 切换按钮 | v-model, variant(default/outline), size, disabled |
| EToggleGroup | 切换按钮组 | v-model, type(single/multiple), variant, size, disabled |
| EButtonGroup | 按钮组 | orientation(horizontal/vertical) |
| EItem | 列表项 | variant(default/outline/muted), size(default/sm), as |
| EAspectRatio | 宽高比容器 | ratio |
| EAffix | 固钉 | offset, position(top/bottom) |
| EWatermark | 水印 | content, fontSize, rotate, gap, opacity |
| EChartContainer | 图表容器 | config(ChartConfig), id |

### 业务组件

| 组件 | 用途 | 关键 Props |
|------|------|-----------|
| EDataPage | 数据列表页 | columns(TableColumn[]), fetchFn(async), searchable, pageSize。内置表格 + 分页 + 搜索 |
| EFormDialog | 表单弹窗 | v-model:open, title, size, loading, confirmText, cancelText |
| EConfirmDialog | 确认弹窗 | v-model:open, title, message, type(info/warning/error), confirmText, cancelText |
| EAdminLayout | 后台管理布局 | logo, title, menuItems(MenuItem[]), v-model:activeKey, v-model:collapsed, headerHeight, sidebarWidth |
| ELoginLayout | 登录页布局 | title, logo, background |
| EAIChat | AI 对话 | messages(ChatMessage[]), loading, placeholder |
| ETimetableGrid | 课程表/时间表 | data(TimetableItem[]), startHour, endHour, days |

---

## Composables

| Composable | 用途 | 返回值 |
|------------|------|--------|
| useMessage() | 全局消息提示 | { success, warning, error, info } — 每个接收 string 或 MessageOptions |
| useNotification() | 通知 | { success, warning, error, info } — 接收 NotificationOptions(title, message, position, duration, onClick, closable) |
| useMessageBox() | 对话确认 | { alert, confirm, prompt } — 返回 Promise<'confirm' \| 'cancel'> |
| useTheme() | 主题管理 | { isDark, theme, setTheme, toggleDark, colorTheme, setColorTheme } |
| useConfigProvider() | 读取全局配置 | { size, zIndex, locale } |
| useFormField() | 表单字段上下文 | { id, name, formItemId, valid, isDirty, isTouched, error }（需在 FormField 内使用） |

## 主题系统

- **Design Tokens**: CSS 自定义属性，定义在 `tokens.css`，前缀 `--`（如 `--primary`, `--background`）
- **暗色模式**: `dark.css`，通过 `<html class="dark">` 切换
- **色彩主题**: 7 种（neutral/blue/green/rose/orange/violet/slate），通过 `useTheme().setColorTheme()` 切换
- **样式工具**: 使用 `cn()` 合并 Tailwind 类名，自动解决冲突

```ts
import { cn } from '@danweiyuan/eui'
cn('px-2 py-1', isActive && 'bg-primary text-white', className)
```

## 通用类型

```ts
type Size = 'sm' | 'default' | 'lg'

interface Option {
  label: string
  value: string | number
  disabled?: boolean
}

interface GroupedOption {
  label: string
  options: Option[]
}

interface MenuItem {
  key: string
  label: string
  icon?: string
  /** Route path for router mode (falls back to key if not provided) */
  path?: string
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

type DatePickerType = 'date' | 'daterange' | 'month' | 'year'

interface DatePickerShortcut {
  text: string
  value: Date | Date[] | (() => Date | Date[])
}

type TabPosition = 'top' | 'bottom' | 'left' | 'right'
```
