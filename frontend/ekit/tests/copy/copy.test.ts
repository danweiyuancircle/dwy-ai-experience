import { describe, it, expect, beforeEach, vi } from 'vitest'
import { copyText, useClipboard } from '@/copy'

const writeTextMock = vi.fn().mockResolvedValue(undefined)

describe('copyText', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })
    writeTextMock.mockClear()
  })

  it('calls navigator.clipboard.writeText with the given text', async () => {
    await copyText('hello')
    expect(writeTextMock).toHaveBeenCalledWith('hello')
  })
})

// useClipboard 行为由 @vueuse/core 保证，此处只做再导出的冒烟测试
describe('useClipboard (re-exported from @vueuse/core)', () => {
  it('is a function', () => {
    expect(typeof useClipboard).toBe('function')
  })

  it('returns { text, copy, copied, isSupported } with ref-like isSupported', () => {
    const result = useClipboard()
    expect(result).toHaveProperty('text')
    expect(result).toHaveProperty('copy')
    expect(result).toHaveProperty('copied')
    expect(result).toHaveProperty('isSupported')
    expect(result.isSupported).toHaveProperty('value')
    expect(typeof result.copy).toBe('function')
  })
})
