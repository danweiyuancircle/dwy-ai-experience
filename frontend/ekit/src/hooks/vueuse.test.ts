import { describe, it, expect } from 'vitest'
import { isRef } from 'vue'
import {
  useThrottle,
  useWindowSize,
  useMediaQuery,
  useIntersectionObserver,
  useResizeObserver,
} from './vueuse'

describe('vueuse re-exports', () => {
  it('useWindowSize returns width and height refs', () => {
    const { width, height } = useWindowSize()
    expect(isRef(width)).toBe(true)
    expect(isRef(height)).toBe(true)
  })

  it('useMediaQuery returns a boolean ref', () => {
    const result = useMediaQuery('(min-width: 768px)')
    expect(isRef(result)).toBe(true)
    expect(typeof result.value).toBe('boolean')
  })

  it('useThrottle is a function', () => {
    expect(typeof useThrottle).toBe('function')
  })

  it('useIntersectionObserver is a function', () => {
    expect(typeof useIntersectionObserver).toBe('function')
  })

  it('useResizeObserver is a function', () => {
    expect(typeof useResizeObserver).toBe('function')
  })
})
