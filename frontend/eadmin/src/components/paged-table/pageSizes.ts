/**
 * 列表壳默认的每页条数选项。
 *
 * 默认值对齐当前各列表接口的 page_size 枚举。别的产品后端限额不同时，
 * 用 PagedTable 的 pageSizes 覆盖，不要改这个常量。
 */
export const LIST_PAGE_SIZES = [20, 50, 100] as const

/** 列表初始每页条数，与后端共享分页默认值一致。 */
export const DEFAULT_LIST_PAGE_SIZE = 50
