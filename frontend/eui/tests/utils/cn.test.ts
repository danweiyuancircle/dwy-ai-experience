import { describe, it, expect } from 'vitest'
import { cn } from '@/utils/cn'

describe('cn', () => {
  it('merges class strings', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
  })

  it('handles conditional classes via clsx', () => {
    expect(cn('base', false && 'hidden', 'end')).toBe('base end')
    expect(cn('base', true && 'visible', 'end')).toBe('base visible end')
  })

  it('handles arrays', () => {
    expect(cn(['a', 'b'], 'c')).toBe('a b c')
  })

  it('handles objects', () => {
    expect(cn({ 'text-red': true, 'text-blue': false })).toBe('text-red')
  })

  it('resolves Tailwind conflicts via twMerge', () => {
    // Later class should win
    expect(cn('px-2', 'px-4')).toBe('px-4')
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500')
  })

  it('handles undefined and null inputs', () => {
    expect(cn(undefined, null, 'valid')).toBe('valid')
  })

  it('returns empty string for no inputs', () => {
    expect(cn()).toBe('')
  })
})
