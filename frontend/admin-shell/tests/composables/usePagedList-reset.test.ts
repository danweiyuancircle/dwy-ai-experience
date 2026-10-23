/** 重置、主动失效和作用域清理必须共享分页与附属汇总的提交边界。 */
import { effectScope } from 'vue'
import { describe, expect, it } from 'vitest'
import { usePagedList } from '../../src/composables/usePagedList'

/** 手动完成网络请求，不依赖计时器或真正 HTTP。 */
function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: unknown) => void
  const promise = new Promise<T>((done, fail) => { resolve = done; reject = fail })
  return { promise, resolve, reject }
}

type Page = { items: string[]; total: number }

describe('分页重置与生命周期', () => {
  it('reset 恢复初始分页和排序并清空筛选、数据及错误', async () => {
    const failure = new Error('HTTP 503')
    let fail = false
    const list = usePagedList<string>({
      pageSize: 20,
      sortable: new Set(['created_at', 'name']),
      defaultSort: { sortBy: 'created_at', order: 'desc' },
      fetcher: async () => {
        if (fail) throw failure
        return { items: ['loaded'], total: 40 }
      },
    })
    await list.setPageSize(100)
    await list.setSort('name', 'asc')
    await list.load(3, 'alice')
    fail = true
    await list.load()
    expect(list.error.value).toBe(failure)
    list.reset()
    expect(list.page.value).toBe(1)
    expect(list.pageSize.value).toBe(20)
    expect(list.keyword.value).toBe('')
    expect(list.sortBy.value).toBe('created_at')
    expect(list.order.value).toBe('desc')
    expect(list.items.value).toEqual([])
    expect(list.total.value).toBe(0)
    expect(list.loading.value).toBe(false)
    expect(list.error.value).toBeNull()
  })

  it.each(['success', 'failure'] as const)('reset 后旧 %s 不清除新请求 loading 或写回状态', async outcome => {
    const old = deferred<Page>()
    const next = deferred<Page>()
    let calls = 0
    const list = usePagedList<string>({ fetcher: () => ++calls === 1 ? old.promise : next.promise })
    const previous = list.load(2, 'previous')
    list.reset()
    const current = list.load(1, 'current')
    if (outcome === 'success') old.resolve({ items: ['old'], total: 99 })
    else old.reject(new Error('old failure'))
    await previous
    expect(list.loading.value).toBe(true)
    expect(list.items.value).toEqual([])
    expect(list.error.value).toBeNull()
    next.resolve({ items: ['current'], total: 1 })
    await current
    expect(list.items.value).toEqual(['current'])
    expect(list.keyword.value).toBe('current')
    expect(list.total.value).toBe(1)
  })

  it('invalidate 保留已呈现数据，失效请求的失败不能清空它', async () => {
    const pending = deferred<Page>()
    let calls = 0
    const list = usePagedList<string>({ fetcher: async () => ++calls === 1
      ? { items: ['visible'], total: 12 }
      : pending.promise,
    })
    await list.load(2, 'visible')
    const previous = list.load(3)
    list.invalidate()
    expect(list.loading.value).toBe(false)
    pending.reject(new Error('late failure'))
    await previous
    expect(list.items.value).toEqual(['visible'])
    expect(list.total.value).toBe(12)
    expect(list.error.value).toBeNull()
  })

  it('invalidate 保留错误原因，新请求开始时才清错', async () => {
    const failure = new Error('HTTP 503')
    let fail = true
    const list = usePagedList<string>({ fetcher: async () => {
      if (fail) throw failure
      return { items: ['retried'], total: 1 }
    } })
    await list.load()
    list.invalidate()
    expect(list.error.value).toBe(failure)
    fail = false
    const retry = list.load()
    expect(list.error.value).toBeNull()
    await retry
    expect(list.items.value).toEqual(['retried'])
  })

  it('fetcher 的 isCurrent 保护附属汇总，reset 后旧汇总不提交', async () => {
    const old = deferred<Page>()
    const next = deferred<Page>()
    let calls = 0
    let summary = ''
    const list = usePagedList<string>({ fetcher: async (_params, request) => {
      const result = await (++calls === 1 ? old.promise : next.promise)
      if (request.isCurrent()) summary = result.items[0]
      return result
    } })
    const previous = list.load()
    list.reset()
    const current = list.load()
    next.resolve({ items: ['current'], total: 1 })
    await current
    old.resolve({ items: ['old'], total: 22 })
    await previous
    expect(summary).toBe('current')
    expect(list.items.value).toEqual(['current'])
  })

  it.each(['success', 'failure'] as const)('scope 销毁淘汰 %s 并停止 loading 与附属提交', async outcome => {
    const pending = deferred<Page>()
    let summary = ''
    const scope = effectScope()
    const list = scope.run(() => usePagedList<string>({ fetcher: async (_params, request) => {
      const result = await pending.promise
      if (request.isCurrent()) summary = result.items[0]
      return result
    } }))!
    const previous = list.load()
    scope.stop()
    expect(list.loading.value).toBe(false)
    if (outcome === 'success') pending.resolve({ items: ['disposed'], total: 42 })
    else pending.reject(new Error('disposed failure'))
    await previous
    expect(list.items.value).toEqual([])
    expect(list.total.value).toBe(0)
    expect(list.error.value).toBeNull()
    expect(summary).toBe('')
  })
})
