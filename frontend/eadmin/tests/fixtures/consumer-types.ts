/** 在独立安装环境编译公开合同，防止只输出 JS 或把泛型退化为 any。 */
import { usePagedList, type PagedListOptions, type PagedListRequest } from '@dwydev/admin-kit/composables'
import { PagedTable, type ConfigFieldSpec } from '@dwydev/admin-kit/components'
import { usePagedList as compatibleList } from '@dwydev/admin-kit/paged-list'

const options: PagedListOptions<number> = {
  fetcher: async ({ page }, request: PagedListRequest) => ({
    items: request.isCurrent() ? [page] : [],
    total: 1,
  }),
}
const list = usePagedList(options)
const compatible = compatibleList<number>({ fetcher: async () => ({ items: [1], total: 1 }) })
const error: unknown = list.error.value
const field: ConfigFieldSpec | undefined = undefined
list.reset()
compatible.invalidate()
// @ts-expect-error 每页条数必须是数字。
void list.setPageSize('twenty')
void [PagedTable, field, error]
