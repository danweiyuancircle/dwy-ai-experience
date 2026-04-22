import { describe, it, expect, vi } from 'vitest'
import { ref, nextTick } from 'vue'
import { useDebounce, useClickOutside, useEventListener } from '@/hooks'

describe('useDebounce (wraps @vueuse/core refDebounced, default 300ms)', () => {
  it('returns initial value immediately', () => {
    const source = ref('hello')
    const debounced = useDebounce(source, 100)
    expect(debounced.value).toBe('hello')
  })

  it('debounces value updates', async () => {
    vi.useFakeTimers()

    const source = ref('initial')
    const debounced = useDebounce(source, 200)

    source.value = 'updated'
    await nextTick()

    expect(debounced.value).toBe('initial')

    await vi.advanceTimersByTimeAsync(200)
    expect(debounced.value).toBe('updated')

    vi.useRealTimers()
  })

  it('only applies the last value during rapid changes', async () => {
    vi.useFakeTimers()

    const source = ref(0)
    const debounced = useDebounce(source, 100)

    source.value = 1
    await nextTick()
    await vi.advanceTimersByTimeAsync(50)

    source.value = 2
    await nextTick()
    await vi.advanceTimersByTimeAsync(50)

    source.value = 3
    await nextTick()
    await vi.advanceTimersByTimeAsync(100)

    expect(debounced.value).toBe(3)

    vi.useRealTimers()
  })

  it('uses default delay of 300ms (ekit override, VueUse default is 200)', async () => {
    vi.useFakeTimers()

    const source = ref('a')
    const debounced = useDebounce(source)

    source.value = 'b'
    await nextTick()

    await vi.advanceTimersByTimeAsync(299)
    expect(debounced.value).toBe('a')

    await vi.advanceTimersByTimeAsync(1)
    expect(debounced.value).toBe('b')

    vi.useRealTimers()
  })
})

describe('useClickOutside (re-exported from @vueuse/core onClickOutside)', () => {
  it('is a function', () => {
    expect(typeof useClickOutside).toBe('function')
  })
})

describe('useEventListener (re-exported from @vueuse/core)', () => {
  it('is a function', () => {
    expect(typeof useEventListener).toBe('function')
  })
})
