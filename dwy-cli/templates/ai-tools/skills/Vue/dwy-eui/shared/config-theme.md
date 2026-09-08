# 配置与主题

- **必须**在 App 根包 `EConfigProvider`（locale / 默认尺寸 / zIndex）。缺了日期英文、z-index 乱、文案回退。
- `locale.name` 用 BCP 47（`zh-CN` / `en-US`），默认 `zh-CN`。
- 类名合并走 `cn()`（clsx + tailwind-merge）。
- 主题走 `useTheme()` 的 `setColorTheme` / `toggleDark`，**不要**手改 `<html class="dark">`。
- 样式入口：`import '@dwydev/eui/theme'`。
- 轻提示用 `useMessage()`，不要当 Toast 再包一层。
