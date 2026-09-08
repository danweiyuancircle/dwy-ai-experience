# @dwydev/eui 2.x

精确签名以安装版本为准（见上级 SKILL.md：先 clone tag，拿不到再读 node_modules）。本页是 2.x 导航与陷阱。

跨大版本不变的表单 / 弹层 / reka / 主题在 `shared/`。查 props 走 `lookup.md`。

## Composables

| 名 | 用途 | 下限 |
|----|------|------|
| `useMessage` | 轻提示 success / error / warning / info | |
| `useNotification` | 带标题通知 | |
| `useMessageBox` | alert / confirm / prompt，返回 Promise | |
| `useTheme` | 亮暗与色板 | |
| `useConfigProvider` | size / zIndex / locale | |
| `useFormField` | EFormItem 内 id / error；表单外 `null` | 2.4 起不依赖 vee-validate FormField |
| `useSecureValue` | 密码不写进 HTML attribute | |
| `useEuiMobile` | `max-width: 767` 是否手机布局 | ≥2.4 |

2.4.0-beta.8 **删除** `useToast`，改 `useMessage`。

## 组件导航（只列名）

用途一句话够导航；props 读 types.d.ts。

**展示**：EButton、EButtonGroup、EBadge、EAlert、ECard、ELabel、ESeparator、ETypography、EKbd、ESpinner、EProgress、ESkeleton、EEmpty、EAvatar、EImage、EAspectRatio、EAffix、EWatermark

**表单**：EForm / EFormItem、EField、EInput、EInputGroup、ETextarea、ENumberField、ESelect、ENativeSelect、ECombobox、EAutocomplete、ECheckbox、ERadio、ESwitch、ETagsInput、EDatePicker、ETimePicker、EColorPicker、ERate、ESlider、ECascader、ETreeSelect、EMention、EPinInput（OTP 用 `otp` + `mask`）、EUpload、ETransfer

**数据**：ETable（`virtual` 走 TanStack Virtual）、EDescriptions、ETimeline、EStatistic、ETree、ECalendar、ERangeCalendar、EPagination、EBreadcrumb

**弹层**：EDialog、EDrawer、ESheet、EAlertDialog、ETooltip、EPopover、EHoverCard、EToast（Toaster 挂载点）、EContextMenu、EFormDialog、EConfirmDialog

**布局**：ETabs、EMenu、EDropdown、EAccordion、ECollapsible、EStepper、ECarousel、EScrollArea、EInfiniteScroll、EToggle / EToggleGroup、EItem、EResizable*、ECommand*、ENavigationMenu*、EMenubar*、EAdminLayout、EConfigProvider

已删组件见 `breaking.md`，不要再 import。

## 2.x 陷阱

### 汉堡 / 抽屉

- `ESheet` / `EAdminLayout` 的 Boolean `open` / `mobileOpen` **缺省必须是 `undefined`**，不能是 `false`。`false` 会让非受控开关永远打不开（≥2.4.0-beta.6）。
- 关闭态 overlay 必须卸掉（`unmountOnHide`），否则挡住汉堡。
- 打开态 overlay 用 `EConfigProvider.zIndex`（默认 2000），压过应用顶栏 `z-50`（≥2.4.0-beta.10）。
- 手机抽屉打开时 `EAdminLayout` 把 header 槽设 `invisible`，避免用户名和关闭钮抢角（≥2.4.0-beta.11）。

### ETable

- 列 `width` 用数字 px，不要百分比。表 `minWidth` = 列宽之和：宽于容器横滑，窄于容器铺满（≥2.4.0-beta.9）。
- 不要再上 `EVirtualTable`，用 `ETable` 的 `virtual`。
- 排序对外仍 `@sort` + `TableColumn.sortable`。

### 手机布局

- 断点与 Tailwind `md` 对齐：`max-width: 767`。`useEuiMobile()` 与 `EAdminLayout` / `EPagination` 同一套。
