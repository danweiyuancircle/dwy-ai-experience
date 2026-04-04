import { vi } from 'vitest'
import { copyText, useClipboard } from './index'

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

describe('useClipboard', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })
    writeTextMock.mockClear()
  })

  it('has isSupported true when clipboard is available', () => {
    const { isSupported } = useClipboard()
    expect(isSupported).toBe(true)
  })

  it('updates text and copied after copy', async () => {
    const { text, copied, copy } = useClipboard()

    expect(text.value).toBe('')
    expect(copied.value).toBe(false)

    await copy('copied text')

    expect(writeTextMock).toHaveBeenCalledWith('copied text')
    expect(text.value).toBe('copied text')
    expect(copied.value).toBe(true)
  })

  it('resets copied to false after 1500ms', async () => {
    vi.useFakeTimers()

    const { copied, copy } = useClipboard()
    await copy('test')

    expect(copied.value).toBe(true)

    vi.advanceTimersByTime(1500)
    expect(copied.value).toBe(false)

    vi.useRealTimers()
  })

  it('returns isSupported false when clipboard is unavailable', () => {
    // Temporarily remove clipboard
    const original = navigator.clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: undefined,
      writable: true,
      configurable: true,
    })

    const { isSupported } = useClipboard()
    expect(isSupported).toBe(false)

    // Restore
    Object.defineProperty(navigator, 'clipboard', {
      value: original,
      writable: true,
      configurable: true,
    })
  })

  it('does nothing when isSupported is false', async () => {
    const original = navigator.clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: undefined,
      writable: true,
      configurable: true,
    })

    const { text, copied, copy } = useClipboard()
    await copy('should not work')

    expect(text.value).toBe('')
    expect(copied.value).toBe(false)

    Object.defineProperty(navigator, 'clipboard', {
      value: original,
      writable: true,
      configurable: true,
    })
  })
})
