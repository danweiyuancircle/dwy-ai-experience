/**
 * 面包屑推导：meta.breadcrumb 优先，否则 matched 上带 title 的链。
 * 仅一项时调用方通常隐藏面包屑（避免无意义导航）。
 */
import { computed, type ComputedRef } from 'vue'
import { useRoute } from 'vue-router'
import type { AdminBreadcrumbItem } from '../model/types'

/**
 * 从当前路由推导面包屑 items。
 *
 * Returns:
 *   ComputedRef&lt;AdminBreadcrumbItem[]&gt;: 面包屑列表；可能为空或仅一项。
 */
export function useAdminBreadcrumb(): ComputedRef<AdminBreadcrumbItem[]> {
  const route = useRoute()
  return computed(() => {
    const override = route.meta.breadcrumb
    if (Array.isArray(override) && override.length > 0) {
      return override.map((item) => ({
        label: item.label,
        to: item.to,
      }))
    }

    const items: AdminBreadcrumbItem[] = []
    for (const record of route.matched) {
      const title = record.meta.title
      if (typeof title !== 'string' || !title) continue
      const path = record.path
      // 末项在渲染时不需要 to；这里先全部带 path，渲染层对最后一项去链接
      items.push({
        label: title,
        to: path && path !== '' ? (path.startsWith('/') ? path : `/${path}`) : undefined,
      })
    }

    // 单页 matched 只有自身时，去掉 to（当前页不可点）
    if (items.length === 1) {
      return [{ label: items[0].label }]
    }
    if (items.length > 1) {
      const last = items[items.length - 1]
      return [
        ...items.slice(0, -1),
        { label: last.label },
      ]
    }
    return items
  })
}
