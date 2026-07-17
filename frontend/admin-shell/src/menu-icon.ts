/**
 * lucide 图标组件 → MenuItem.icon 类型断言
 * eui MenuItem.icon 声明为 string，实际 EMenu 支持组件；统一在此收口断言。
 */

/**
 * 将图标组件断言为 MenuItem 可用的 icon 类型。
 *
 * Args:
 *   icon (unknown): lucide-vue-next 等图标组件。示例：`LayoutDashboard`。
 * Returns:
 *   string: 仅类型层面的 string（运行时仍是组件）。
 */
export function asMenuIcon(icon: unknown): string {
  return icon as string
}
