/**
 * 侧栏激活 key：优先 meta.menuKey，否则 route.path。
 * 嵌套子页通过 menuKey 高亮父级叶子菜单。
 */
import { computed, type ComputedRef } from 'vue'
import { useRoute } from 'vue-router'

/**
 * 计算当前侧栏应高亮的 menu key。
 *
 * Returns:
 *   ComputedRef&lt;string&gt;: 与 MenuItem.key 对齐的激活 key。
 */
export function useAdminActiveKey(): ComputedRef<string> {
  const route = useRoute()
  return computed(() => {
    const menuKey = route.meta.menuKey
    if (typeof menuKey === 'string' && menuKey.length > 0) {
      return menuKey
    }
    return route.path
  })
}
