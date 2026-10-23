/** 兼容原有产品的 paged-list 子路径，状态机与 composables 入口共享同一实现。 */
export { usePagedList } from '../composables/usePagedList'
export type {
  PagedListOptions,
  PagedListSort,
  PagedListFetcherParams,
  PagedListFetcherResult,
  PagedListRequest,
} from '../composables/usePagedList'
