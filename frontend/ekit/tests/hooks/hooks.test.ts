import { describe, it, expect, vi } from 'vitest'
import { ref, nextTick } from 'vue'
import { useDebounce } from '@/hooks'

describe('useDebounce', () => {
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

    // Before delay, still old value
    expect(debounced.value).toBe('initial')

    // After delay, updated
    vi.advanceTimersByTime(200)
    expect(debounced.value).toBe('updated')

    vi.useRealTimers()
  })

  it('only applies the last value during rapid changes', async () => {
    vi.useFakeTimers()

    const source = ref(0)
    const debounced = useDebounce(source, 100)

    source.value = 1
    await nextTick()
    vi.advanceTimersByTime(50)

    source.value = 2
    await nextTick()
    vi.advanceTimersByTime(50)

    source.value = 3
    await nextTick()
    vi.advanceTimersByTime(100)

    expect(debounced.value).toBe(3)

    vi.useRealTimers()
  })

  it('uses default delay of 300ms', async () => {
    vi.useFakeTimers()

    const source = ref('a')
    const debounced = useDebounce(source)

    source.value = 'b'
    await nextTick()

    vi.advanceTimersByTime(299)
    expect(debounced.value).toBe('a')

    vi.advanceTimersByTime(1)
    expect(debounced.value).toBe('b')

    vi.useRealTimers()
  })
})
