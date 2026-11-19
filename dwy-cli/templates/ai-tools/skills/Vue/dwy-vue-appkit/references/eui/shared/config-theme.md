# 配置与主题

- **必须**在 App 根包 `EConfigProvider`（locale / 默认尺寸 / zIndex）。缺了日期英文、z-index 乱、文案回退。
- `locale.name` 用 BCP 47（`zh-CN` / `en-US`），默认 `zh-CN`。
- `locale.name` 控制日历日期格式，不自动翻译 UI 文案；扁平文案表支持局部覆盖并与默认中文合并。
- `EDatePicker` 的 `datePickerPlaceholder`（日期/月/年）、`datePickerStartPlaceholder`、`datePickerEndPlaceholder`、`datePickerRangeSeparator` 默认依次为「请选择日期 / 开始日期 / 结束日期 / 至」，运行期更新立即生效。组件 `placeholder`、`startPlaceholder`、`endPlaceholder`、`rangeSeparator` 显式值优先，包括空串；分隔符同时用于空态和已选值。
- 类名合并走 `cn()`（clsx + tailwind-merge）。
- 主题走 `useTheme()` 的 `setColorTheme` / `toggleDark`，**不要**手改 `<html class="dark">`。
- 样式入口：`import '@dwydev/eui/theme'`。
- 轻提示用 `useMessage()`，不要当 Toast 再包一层。
