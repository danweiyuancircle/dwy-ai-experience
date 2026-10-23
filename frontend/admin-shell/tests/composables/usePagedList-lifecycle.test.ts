/** 合并两消费方的失败反馈与异步失效合同。 */
import { describe, expect, it, vi } from 'vitest'
import { usePagedList } from '../../src/composables/usePagedList'

/** 异步响应顺序由用户输入决定，迟到请求不得覆盖当前筛选结果。 */
describe('usePagedList 请求顺序与失败状态', () => {
  /** 人工控制 API 完成顺序，复现真实网络竞态。 */
  function deferred<T>() {
    let resolve!: (value: T) => void
    let reject!: (error: unknown) => void
    const promise = new Promise<T>((done, fail) => { resolve = done; reject = fail })
    return { promise, resolve, reject }
  }

  it('迟到成功结果不覆盖最近一次搜索，也不提前清除 loading', async () => {
    const first = deferred<{ items: string[]; total: number }>()
    const second = deferred<{ items: string[]; total: number }>()
    const fetcher = vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise)
    const list = usePagedList<string>({ fetcher })
    const oldRequest = list.load(1, 'old')
    const newRequest = list.load(2, 'new')
    first.resolve({ items: ['old'], total: 1 })
    await oldRequest
    expect(list.items.value).toEqual([])
    expect(list.loading.value).toBe(true)
    second.resolve({ items: ['new'], total: 3 })
    await newRequest
    expect(list.items.value).toEqual(['new'])
    expect(list.total.value).toBe(3)
    expect(list.page.value).toBe(2)
    expect(list.loading.value).toBe(false)
    expect(list.error.value).toBeNull()
  })

  it('503 保留失败原因，下一次加载清除旧错误并恢复结果', async () => {
    const failure = new Error('HTTP 503')
    const fetcher = vi.fn().mockRejectedValueOnce(failure).mockResolvedValueOnce({ items: ['ok'], total: 1 })
    const list = usePagedList<string>({ fetcher })
    await list.load()
    expect(list.items.value).toEqual([])
    expect(list.error.value).toBe(failure)
    expect(list.loading.value).toBe(false)
    const retry = list.load()
    expect(list.error.value).toBeNull()
    await retry
    expect(list.items.value).toEqual(['ok'])
    expect(list.error.value).toBeNull()
  })

  it('迟到失败不覆盖最近请求的成功结果或错误状态', async () => {
    const first = deferred<{ items: string[]; total: number }>()
    const fetcher = vi.fn().mockReturnValueOnce(first.promise).mockResolvedValueOnce({ items: ['new'], total: 2 })
    const list = usePagedList<string>({ fetcher })
    const oldRequest = list.load()
    await list.load(2)
    first.reject(new Error('late 503'))
    await oldRequest
    expect(list.items.value).toEqual(['new'])
    expect(list.total.value).toBe(2)
    expect(list.error.value).toBeNull()
  })

  it('invalidate 阻止卸载或产品切换后迟到请求回写', async () => {
    const pending = deferred<{ items: string[]; total: number }>()
    const list = usePagedList<string>({ fetcher: () => pending.promise })
    const request = list.load()
    list.invalidate()
    expect(list.loading.value).toBe(false)
    pending.resolve({ items: ['stale'], total: 3 })
    await request
    expect(list.items.value).toEqual([])
    expect(list.total.value).toBe(0)
    expect(list.error.value).toBeNull()
  })
  it('较新请求先成功后，较旧成功仍不能覆盖页面', async () => {
    const first = deferred<{ items: string[]; total: number }>()
    const fetcher = vi.fn().mockReturnValueOnce(first.promise).mockResolvedValueOnce({ items: ['new'], total: 2 })
    const list = usePagedList<string>({ fetcher })
    const oldRequest = list.load()
    await list.load(2)
    first.resolve({ items: ['old'], total: 1 })
    await oldRequest
    expect(list.items.value).toEqual(['new'])
    expect(list.total.value).toBe(2)
    expect(list.loading.value).toBe(false)
  })

  it('失效后的旧失败不污染状态，并允许再次加载', async () => {
    const pending = deferred<{ items: string[]; total: number }>()
    const fetcher = vi.fn().mockReturnValueOnce(pending.promise).mockResolvedValueOnce({ items: ['next'], total: 1 })
    const list = usePagedList<string>({ fetcher })
    const request = list.load()
    list.invalidate()
    pending.reject(new Error('old product failed'))
    await request
    expect(list.error.value).toBeNull()
    expect(list.loading.value).toBe(false)
    await list.load()
    expect(list.items.value).toEqual(['next'])
    expect(list.total.value).toBe(1)
  })
})
