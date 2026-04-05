# @danweiyuan/eui

## 1.2.3

### Patch Changes

- Toast 组件新增 `useToast` composable 封装，替代直接暴露 vue-sonner 的 `toast` 函数
- 移除 Sidebar 组件（改用 EMenu + EAdminLayout 构建布局）
- EConfigProvider 支持国际化，透传 locale 到 reka-ui
- 修复 DatePicker 月份/年份选择器渲染错误

## 1.2.2

### Patch Changes

- 移除 vaul-vue 依赖，EDrawer 用 reka-ui Dialog 重写，解决 @vueuse/core v10/v14 版本冲突导致 Vite 8 构建失败

## 1.2.1

### Patch Changes

- 主题 CSS 内置 `@source` 指令，消费者 `@import "@danweiyuan/eui/theme"` 后自动扫描组件类名，无需手动配置

## 1.2.0

### Minor Changes — Phase 2+3 组件增强（14 组件，40+ 新特性）

**Phase 2:**

- **Table** — 虚拟滚动、列拖拽调整宽度
- **Tree** — 懒加载 `loadFn`、拖拽排序 `node-drop`、`filterMethod`、`checkStrictly`
- **Cascader** — 懒加载 `loadFn`、多选 + `collapseTags`
- **Tabs** — `closable`、`addable`、`tabPosition`（top/bottom/left/right）
- **Menu** — 路由模式、`uniqueOpened`、`defaultOpeneds`
- **Select** — 远程搜索 `remoteMethod` + `loading`
- **Textarea** — `showWordLimit`、`autoResize` minRows/maxRows

**Phase 3:**

- **Dropdown** — `trigger`（hover/click）、`splitButton` 模式
- **Pagination** — 跳转、`layout` 自定义、`disabled`
- **NumberField** — `precision`、`controlsPosition`（right）、`placeholder`、`readonly`
- **Checkbox** — group 模式 `options`、`border` 样式、`direction`
- **Radio** — `optionType`（button 分段组）、`border`、`size`
- **Dialog** — `destroyOnClose`
- **useNotification** — `onClick` 回调、`closable` 切换

## 1.1.0

### Minor Changes — Phase 1 组件增强（7 组件，25+ 新特性）

- **Select** — 可搜索 `filterable`、多选 `multiple`、`collapseTags`
- **Table** — 固定列（sticky）、可展开行、`rowClassName`、合计行
- **Input** — `showWordLimit` 字符计数、prefix/suffix 插槽定位修复
- **Dialog** — `draggable`、`closeOnClickModal`、`closeOnPressEscape`、`fullscreen`
- **Form** — `inline` 模式、`validateField(name)` API
- **DatePicker** — type 变体（date/daterange/month/year）、`disabledDate`、`shortcuts`、范围模式
- **Upload** — `beforeUpload` 钩子、预览 emit、上传进度条、`autoUpload`、`headers`、`withCredentials`

## 1.0.2

### Patch Changes

- 修复 Transfer 组件：替换 `ref<Set>` 为 `ref<Array>` 解决 Vue 响应性兼容问题
- 修复 Transfer 组件：checkbox 添加 `@click.stop` 防止双次切换
- 修复 Accordion 组件：移除插槽名称中多余的 `panel-` 前缀

## 1.0.1

### Patch Changes

- 修复 EButton click 事件通过 reka-ui as-child 未传播（影响 Dialog、Popover、Dropdown 触发器）
- 修复 EDialog/EPopover/ESheet 与 reka-ui 受控模式的 open 状态管理
- 修复 Toast（vue-sonner）CSS 未加载，toast 不可见
- 统一图标为 LoaderCircle，替换原始 CSS spinner
- 新增 7 种颜色主题预设（Blue、Green、Rose、Orange、Violet、Slate）
- 新增暗色模式支持（`useTheme` composable）
- 修复 15+ 组件 bug（ESelect valueKey/labelKey、EInput iOS Safari、ETabs 非受控模式等）

## 1.0.0

首次发布。89 个 Vue 3 组件，基于 Reka-ui 原语层 + shadcn-vue 设计风格 + Element Plus 式 API。
