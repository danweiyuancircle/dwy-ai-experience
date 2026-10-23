/**
 * 分页列表状态机 composable(业务无关)
 *
 * 收口"分页 + 关键词 + 排序 + 每页条数"的同构列表状态:page / pageSize / total /
 * items / loading 的流转与失败清空行为只写一次,业务侧注入 fetcher。
 * 与 eui EPagination 直连:全部状态都是 ref,storeToRefs 解构不丢响应性。
 *
 * 设计约定(与既有 store 行为逐条对齐):
 * - fetcher 抛错 → 清空 items / total,保留 error，不向上抛；由宿主呈现失败
 * - keyword 空白不传给 fetcher;省略 keyword 参数时沿用当前值
 * - 排序可选:传 sortable 才生效;setSort 恒导出(未配时 no-op),白名单外 / 空方向回默认排序
 */
import { getCurrentScope, onScopeDispose, ref, shallowRef } from 'vue'
import { DEFAULT_LIST_PAGE_SIZE } from '../components/paged-table/pageSizes'

/** 排序状态 */
export interface PagedListSort {
  /** 排序字段名(列 key)。示例:``'created_at'``。 */
  sortBy: string
  /** 升降序。枚举 ``{'asc', 'desc'}``。示例:``'desc'``。 */
  order: 'asc' | 'desc'
}

/** fetcher 收到的请求参数(空值字段已被剔除语义,见 usePagedList) */
export interface PagedListFetcherParams {
  /** 页码,从 1。示例:``1``。 */
  page: number
  /** 每页条数。示例:``50``。 */
  pageSize: number
  /** 关键词(已去首尾空白,空白时不传)。示例:``'alice'``。 */
  keyword?: string
  /** 排序字段(仅 sortable 配置时出现)。 */
  sortBy?: string
  /** 升降序(仅 sortable 配置时出现)。 */
  order?: 'asc' | 'desc'
}

/** fetcher 返回的分页结果 */
export interface PagedListFetcherResult<T> {
  /** 当前页数据;undefined 兜底为空数组。 */
  items: T[]
  /** 总条数。示例:``100``。 */
  total: number
}

/** 当前分页请求向附属汇总提供的提交边界。 */
export interface PagedListRequest {
  /** 附属汇总回写前检查；重置、主动失效或销毁作用域后返回 false。 */
  isCurrent: () => boolean
}

/** 分页行为配置；fetcher 也兼容只接收 params 的既有实现。 */
export interface PagedListOptions<T> {
  /** 拉一页数据的异步函数(业务 API 调用收口在这里)。 */
  fetcher: (params: PagedListFetcherParams, request: PagedListRequest) => Promise<PagedListFetcherResult<T>>
  /** 初始每页条数,默认 50;须与后端 page_size 枚举对齐。示例:``50``。 */
  pageSize?: number
  /** 可排序字段白名单;传入才启用排序功能。示例:``new Set(['created_at'])``。 */
  sortable?: Set<string>
  /** 默认排序(白名单外 / 空方向回退到这里);配 sortable 时建议提供。 */
  defaultSort?: PagedListSort
}

/**
 * 创建分页列表状态机。
 *
 * @param options fetcher 与可选排序配置。
 * @returns 响应式状态与操作方法;全部状态均为 ref,可直接被 pinia setup store 展开。
 */
export function usePagedList<T>(options: PagedListOptions<T>) {
  const { fetcher, sortable, defaultSort } = options

  const page = ref(1)
  // 必须是 ref:storeToRefs 会丢掉普通数字,EPagination 就会用默认 10
  const pageSize = ref(options.pageSize ?? DEFAULT_LIST_PAGE_SIZE)
  const total = ref(0)
  const items = ref<T[]>([])
  const loading = ref(false)
  const keyword = ref('')
  /** 浅引用保留原始错误及其 HTTP 状态，避免把失败当作正常空列表。 */
  const error = shallowRef<unknown | null>(null)

  // 排序状态始终存在(供 fetcher 参数使用);仅当配置 sortable 才暴露 setSort
  const sortBy = ref(defaultSort?.sortBy ?? '')
  const order = ref<'asc' | 'desc'>(defaultSort?.order ?? 'desc')
  /** 单调请求序号，同时用于会话重置与组件销毁后的响应失效。 */
  let requestVersion = 0
  if (getCurrentScope()) onScopeDispose(invalidate)

  /** 淘汰在途请求并停止 loading，保留已呈现数据、筛选与错误；不取消底层 HTTP。 */
  function invalidate(): void {
    requestVersion += 1
    loading.value = false
  }

  /** 清空分页与筛选，并使旧请求的成功、失败、finally 均失效。 */
  function reset() {
    invalidate()
    page.value = 1
    pageSize.value = options.pageSize ?? DEFAULT_LIST_PAGE_SIZE
    total.value = 0
    items.value = []
    loading.value = false
    keyword.value = ''
    error.value = null
    sortBy.value = defaultSort?.sortBy ?? ''
    order.value = defaultSort?.order ?? 'desc'
  }

  /**
   * 拉一页。
   * @param nextPage 页码,从 1。取值 ``[1, ∞)``。示例:``1``。
   * @param nextKeyword 搜索词;省略沿用当前,传空串清空。示例:``'alice'``。
   */
  async function load(nextPage = 1, nextKeyword?: string) {
    const version = ++requestVersion
    error.value = null
    /** fetcher 的汇总和分页共享同一提交边界。 */
    const isCurrent = () => version === requestVersion
    if (nextKeyword !== undefined) keyword.value = nextKeyword
    page.value = nextPage
    loading.value = true
    try {
      const q = keyword.value.trim()
      const params: PagedListFetcherParams = { page: page.value, pageSize: pageSize.value }
      if (q) params.keyword = q
      if (sortable) {
        params.sortBy = sortBy.value
        params.order = order.value
      }
      const result = await fetcher(params, { isCurrent })
      if (!isCurrent()) return
      items.value = result.items ?? []
      total.value = result.total
    } catch (cause) {
      if (!isCurrent()) return
      // 原始原因由宿主呈现；不向上抛，保留既有调用方式。
      items.value = []
      total.value = 0
      error.value = cause
    } finally {
      if (isCurrent()) loading.value = false
    }
  }

  /**
   * 改排序并从第 1 页重拉。字段不在白名单或 direction 为空 → 回默认排序。
   * 未配置 sortable 时为 no-op(恒导出,调用方无需判空)。
   * @param key 列 key。示例:``'created_at'``。
   * @param direction 升降序;null 取消。枚举 ``{'asc', 'desc'}``。示例:``'desc'``。
   */
  async function setSort(key: string, direction: 'asc' | 'desc' | null): Promise<void> {
    if (!sortable) return
    if (!direction || !sortable.has(key)) {
      sortBy.value = defaultSort?.sortBy ?? ''
      order.value = defaultSort?.order ?? 'desc'
    } else {
      sortBy.value = key
      order.value = direction
    }
    await load(1)
  }

  /**
   * 改每页条数并从第 1 页重拉。选项由页面按后端 page_size 上限传入。
   * @param size 每页条数。示例:``100``。
   */
  async function setPageSize(size: number) {
    pageSize.value = size
    await load(1)
  }

  return {
    page,
    pageSize,
    total,
    items,
    loading,
    keyword,
    error,
    sortBy,
    order,
    load,
    reset,
    invalidate,
    setSort,
    setPageSize,
  }
}
