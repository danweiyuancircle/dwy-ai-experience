/**
 * usePagedList 分页列表状态机单测
 *
 * 收口 traffic / admin-users / usage / admin-announcements 四份同构分页逻辑。
 * 只测纯逻辑(fetcher 用假实现),HTTP 层由 apps/web 的 store 测试覆盖。
 */
import { describe, expect, it, vi } from 'vitest'
import { usePagedList } from '../../src/composables/usePagedList'

describe('usePagedList 请求竞争', () => {
  it.each(['success', 'failure'])('旧请求 %s 不影响最新请求的 loading 与数据', async (outcome) => {
    let resolveOld!: (value: { items: number[]; total: number }) => void
    let rejectOld!: (reason: Error) => void
    let resolveNew!: (value: { items: number[]; total: number }) => void
    const old = new Promise<{ items: number[]; total: number }>((resolve, reject) => { resolveOld = resolve; rejectOld = reject })
    const next = new Promise<{ items: number[]; total: number }>((resolve) => { resolveNew = resolve })
    const list = usePagedList<number>({ fetcher: vi.fn().mockReturnValueOnce(old).mockReturnValueOnce(next) })
    const first = list.load(1, 'old')
    const second = list.load(2, 'new')
    if (outcome === 'success') resolveOld({ items: [1], total: 1 })
    else rejectOld(new Error('old failure'))
    await first
    expect(list.loading.value).toBe(true)
    expect(list.items.value).toEqual([])
    resolveNew({ items: [2], total: 2 })
    await second
    expect(list.items.value).toEqual([2])
    expect(list.total.value).toBe(2)
    expect(list.loading.value).toBe(false)
  })
})

interface Row {
  id: number
}

/** 构造可编程 fetcher:记录入参,返回可编程结果 */
function makeFetcher(result?: Partial<{ items: Row[]; total: number }>) {
  const calls: Array<{ page: number; pageSize: number; keyword?: string; sortBy?: string; order?: string }> = []
  const fetcher = vi.fn(async (params: { page: number; pageSize: number; keyword?: string; sortBy?: string; order?: string }) => {
    calls.push(params)
    return { items: [{ id: params.page }] as Row[], total: result?.total ?? 100 }
  })
  return { fetcher, calls }
}

describe('usePagedList 基础分页', () => {
  it('load 拉一页并回填状态', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher, pageSize: 50 })
    await list.load(2)
    expect(list.page.value).toBe(2)
    expect(list.pageSize.value).toBe(50)
    expect(list.items.value).toEqual([{ id: 2 }])
    expect(list.total.value).toBe(100)
    expect(list.loading.value).toBe(false)
    expect(calls[0]).toMatchObject({ page: 2, pageSize: 50 })
  })

  it('load 缺省从第 1 页', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher })
    await list.load()
    expect(calls[0].page).toBe(1)
    expect(list.pageSize.value).toBe(50) // 默认每页 50，显式选项仍支持 20
  })

  it('fetcher 抛错时清空列表不炸,loading 复位', async () => {
    const fetcher = vi.fn(async () => {
      throw new Error('boom')
    })
    const list = usePagedList<Row>({ fetcher })
    await list.load(1)
    expect(list.items.value).toEqual([])
    expect(list.total.value).toBe(0)
    expect(list.loading.value).toBe(false)
  })

  it('items 为空兜底:fetcher 返回 items undefined 时不产生 undefined', async () => {
    const fetcher = vi.fn(async () => ({ items: undefined as unknown as Row[], total: 0 }))
    const list = usePagedList<Row>({ fetcher })
    await list.load(1)
    expect(list.items.value).toEqual([])
  })
})

describe('usePagedList keyword', () => {
  it('load 第二参设置 keyword,请求携带去空白后的值', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher })
    await list.load(1, '  alice ')
    expect(list.keyword.value).toBe('  alice ')
    expect(calls[0].keyword).toBe('alice')
  })

  it('keyword 空白不传给 fetcher', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher })
    await list.load(1, '   ')
    expect(calls[0].keyword).toBeUndefined()
  })

  it('省略 keyword 时沿用当前值', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher })
    await list.load(1, 'bob')
    await list.load(2)
    expect(calls[1].keyword).toBe('bob')
  })
})

describe('usePagedList 排序', () => {
  it('setSort 合法字段生效并回第 1 页', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({
      fetcher,
      sortable: new Set(['created_at', 'bytes_total']),
      defaultSort: { sortBy: 'bytes_total', order: 'desc' },
    })
    await list.setSort('created_at', 'asc')
    expect(list.sortBy.value).toBe('created_at')
    expect(list.order.value).toBe('asc')
    expect(calls[0]).toMatchObject({ page: 1, sortBy: 'created_at', order: 'asc' })
  })

  it('setSort 非法字段 / 空方向回默认排序', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({
      fetcher,
      sortable: new Set(['created_at']),
      defaultSort: { sortBy: 'bytes_total', order: 'desc' },
    })
    await list.setSort('created_at', 'asc') // 先偏离默认
    await list.setSort('hacker_field', 'asc') // 非白名单
    expect(list.sortBy.value).toBe('bytes_total')
    expect(list.order.value).toBe('desc')
    await list.setSort('created_at', null) // 取消排序
    expect(list.sortBy.value).toBe('bytes_total')
    expect(list.order.value).toBe('desc')
  })

  it('未配 sortable 时 setSort 为 no-op,fetcher 不收排序参数', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher })
    await list.setSort('created_at', 'asc')
    expect(calls).toHaveLength(0) // no-op 不触发请求
    await list.load(1)
    expect(calls[0].sortBy).toBeUndefined()
    expect(calls[0].order).toBeUndefined()
  })
})

describe('usePagedList pageSize', () => {
  it('setPageSize 改每页条数并回第 1 页', async () => {
    const { fetcher, calls } = makeFetcher()
    const list = usePagedList<Row>({ fetcher, pageSize: 20 })
    await list.load(3)
    await list.setPageSize(100)
    expect(list.pageSize.value).toBe(100)
    expect(list.page.value).toBe(1)
    expect(calls[1]).toMatchObject({ page: 1, pageSize: 100 })
  })
})
