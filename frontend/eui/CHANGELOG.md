# @dwydev/eui

## 2.4.0-beta.1

### Minor Changes

- **useEuiMobile / EConfigProvider.mobileBreakpoint**：共用手机断点（默认 767，对齐 Tailwind `md`）。`EAdminLayout` / `EPagination` / `ETooltip` 都走这一处，避免各写一遍 media query
- **EAdminLayout**：窄屏默认 `mobileMode="drawer"`，侧栏改为左侧 `ESheet` 覆层，不占主栏宽度。汉堡只切 `mobileOpen`，与桌面 `collapsed` 独立。点菜单后自动关抽屉。`mobileMode="none"` 可关
- **EPagination**：新增 `mode`（`auto` / `simple` / `full`）。默认 `auto`：窄屏只留上一页 / 当前页 / 下一页
- **ETabs**：横向标签条外包 `overflow-x-auto`，多 Tab 在窄屏横滑而不是撑开页面
- **ETooltip**：新增 `trigger`（`auto` / `hover` / `click`）。默认 `auto`：窄屏走 Popover 点击，指针设备仍是 hover
- **ESheet**：新增 `bodyClass`；受控 `open` 改为本地 v-model 同步；无标题时补 `sr-only` 的 DialogTitle，满足无障碍

## 2.3.0

### Minor Changes

- **EPagination**: 去掉首页 / 末页双箭头，只留上一页 / 下一页；页码默认 `show-edges`（省略号 + 末页数字）
- **EPagination**: `pageSizes` 由调用方按后端 `page_size` 上限传入，组件不绑定业务限额
- **EDataPage**: 打开每页条数切换，并透传 `pageSizes`

## 2.2.4

### Patch Changes

- **ERadio**: 选中 number 型 option 时保留原始 number 类型 emit（对齐 `ESelect`），不再强制 `String()` 破坏 v-model 契约
- **EHoverCard**: 移除未实现的 `update:open` 空类型契约（组件仍为非受控 Hover）
- **theme**: `@source` 同步扫描 `src`（monorepo 开发 alias 源码时避免 dist 滞后导致 `rounded-*` 等类缺失）
- **焦点环统一**：表单触发器与可聚焦控件对齐 `ESelect` / `EInput` 标准——`ring-[3px] ring-ring/50`，去掉 `ring-offset-*`（offset 会让环与边框分离，窄控件上尤其明显）。
  - 表单触发器：`ECombobox`、`EDatePicker`、`ETimePicker`、`ECascader`、`ETreeSelect`、`EColorPicker`、`ENumberField`
  - 日历单元格：`EDatePicker` 日/范围/月/年格子
  - 其它：`ETagsInput` 激活 chip、`EAIChat` 输入区、`EAlert` / `EAlertDialog` / `EAdminLayout` 关闭与切换按钮、`EDialog` / `EDrawer` / `ESheet` 关闭按钮、`EResizableHandle`

## 2.2.3

### Patch Changes

- GitHub Release 改为只展示当前版本的 changelog 段落，不再附带 full release notes，便于按版本查看真实发布内容。

## 2.2.2

### Patch Changes

- 增加 GitHub Actions OIDC 发布链路测试版本，支持通过 `@dwydev/eui@x.y.z` tag 自动发布到 npm，并同步创建 GitHub Release。

## 2.2.1

### Patch Changes

- **EMenu**: 修复侧边菜单折叠/展开时文字"闪一下"的问题。内层 `<nav>` 改为 `w-full` 跟随父容器宽度（移除自带的 `transition-[width]` 与写死的 `w-14`/`w-56`），消除与 `EAdminLayout` 侧栏的双层宽度动画及宽度错位；菜单项文字加 `truncate`，避免展开动画期间换行回流。现由父容器单层宽度动画 + `overflow-hidden` 形成平滑的幕布式展开

## 2.1.0

### Minor Changes

- **EDialog**: 新增 `showOverlay` prop（默认 `true`），传 `false` 时不渲染背景遮罩层，背景内容完全可见可交互
- **EDialog**: 默认遮罩样式从 `bg-black/80` 调整为 `bg-black/30 backdrop-blur-sm`，降低不透明度并加入背景模糊，弹框打开时背景内容隐约可见

## 2.0.1

### Patch Changes

- **ECheckbox / EToggle / EMenubarCheckboxItem**: 适配 reka-ui v2 v-model API 改名（`checked`/`pressed` → `modelValue`），修复外层 v-model 不更新导致 UI 看似已勾选但状态未同步的问题
- **测试**: 新增 ECheckbox 点击触发 `update:modelValue` 的回归测试

## 1.3.0

### Minor Changes

- 包名从 `@danweiyuan/eui` 迁移至 `@dwydev/eui`，下游需更新 import 路径和 package.json 依赖
- 同步更新全局规则、CLI 模板、playground 文档中的包名引用

## 1.2.13

### Patch Changes

- **EDialog**: body 内部 wrapper padding 从 `px-0.5`（2px）增加到 `p-1`（4px），修复 focus-ring 被裁切
- **ESheet/EDrawer**: body 增加 `py-1` 垂直内边距，防止首尾元素 focus-ring 被 overflow-auto 裁切

## 1.2.10

### Patch Changes

- **安全修复**: useNotification/useMessageBox innerHTML XSS 漏洞，添加 escapeHtml 转义
- **EInput**: password 类型自动设置 autocomplete="off" / spellcheck="false" / autocorrect="off"
- **EPinInput**: mask 默认值改为 true（安全优先）
- **EDialog**: destroyOnClose 默认值改为 true（关闭即销毁，释放内存）
- **EDrawer**: 新增 destroyOnClose prop，默认 true
- **EPopover**: 新增 destroyOnClose prop，默认 true
- 移除 LoginLayout 组件

## 1.2.9

### Patch Changes

- **ESwitch**: 修复 v-model 不生效问题（根因：reka-ui 用 modelValue 而非 checked）
- **EDialog**: flex 布局 + overflow-hidden 解决内容溢出和 focus ring 裁切
- **EUpload**: 新增 maxSize 文件大小限制、内聚图片预览（动画 + ESC 关闭）、友好错误提示
- **ETimePicker**: HH/MM/OK 改为 locale 中文
- **EPagination**: 移除 w-full 避免独占整行
- **EInputGroup**: 内部 input 去除独立边框圆角，focus-within 统一管理
- **ERate**: 统一三种星星状态 DOM 结构防止 hover 抖动
- **ETagsInput**: 输入重复值时显示友好提示
- **EFormItem**: 控件区域 min-h-9 flex 对齐 Switch 等矮组件，子元素 w-full
- **EStepper**: StepperSeparator 移入 StepperItem 内部修复渲染错误
- **EConfigProvider**: defaultLocale 单一源头，merge 而非替换用户 locale

## 1.2.5

### Patch Changes

- 修复 EToast 样式不生效：vue-sonner CSS 通过 theme/index.css 自动引入，消费者无需额外操作

## 1.2.4

### Patch Changes

- 修复 EToast 消费者项目中 toast 不显示的问题：vue-sonner 从 external 改为内联打包，CSS 样式自动包含
- vue-sonner 从 dependencies 移至 devDependencies，消费者不再需要手动安装

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
