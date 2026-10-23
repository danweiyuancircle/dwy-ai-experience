/**
 * confirmThen：取消不执行；成功和失败各提示一次。
 */
import { describe, expect, it, vi } from 'vitest'
import { confirmThen } from '../../../src/components'

function box(choice: 'confirm' | 'cancel') {
  return { confirm: vi.fn().mockResolvedValue(choice) }
}

function toast() {
  return { success: vi.fn(), error: vi.fn() }
}

describe('confirmThen', () => {
  it('取消时不执行，也不提示', async () => {
    const confirmBox = box('cancel')
    const message = toast()
    const run = vi.fn()

    const ok = await confirmThen(confirmBox, message, {
      message: '确定下架？',
      title: '下架',
      success: '已下架',
      failure: '下架失败',
      run,
    })

    expect(ok).toBe(false)
    expect(confirmBox.confirm).toHaveBeenCalledWith('确定下架？', '下架')
    expect(run).not.toHaveBeenCalled()
    expect(message.success).not.toHaveBeenCalled()
    expect(message.error).not.toHaveBeenCalled()
  })

  it('成功用固定文案提示', async () => {
    const message = toast()
    const run = vi.fn().mockResolvedValue(undefined)

    const ok = await confirmThen(box('confirm'), message, {
      message: '确定？',
      title: '上架',
      success: '已上架',
      failure: '上架失败',
      run,
    })

    expect(ok).toBe(true)
    expect(message.success).toHaveBeenCalledWith('已上架')
  })

  it('成功文案可以用返回值拼', async () => {
    const message = toast()

    await confirmThen(box('confirm'), message, {
      message: '清理？',
      title: '清理缓存',
      failure: '清理失败',
      success: (deleted: number) => `已删除 ${deleted} 条`,
      run: async () => 2,
    })

    expect(message.success).toHaveBeenCalledWith('已删除 2 条')
  })

  it('失败用抛出值生成文案，并且不再向上抛', async () => {
    const message = toast()

    const ok = await confirmThen(box('confirm'), message, {
      message: '确定？',
      title: '退款',
      success: '已退款',
      failure: (error: unknown) => (error instanceof Error ? error.message : '退款失败'),
      run: async () => {
        throw new Error('余额不足')
      },
    })

    expect(ok).toBe(false)
    expect(message.error).toHaveBeenCalledWith('余额不足')
    expect(message.success).not.toHaveBeenCalled()
  })
})
