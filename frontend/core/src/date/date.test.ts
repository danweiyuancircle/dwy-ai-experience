import { describe, it, expect, vi, afterEach } from 'vitest'
import { formatRelativeTime, formatDate, formatDateTime, formatTime } from './index'

describe('formatDate', () => {
  it('formats Date object to YYYY-MM-DD', () => {
    expect(formatDate(new Date(2025, 0, 5))).toBe('2025-01-05')
    expect(formatDate(new Date(2024, 11, 25))).toBe('2024-12-25')
  })

  it('formats timestamp number', () => {
    const ts = new Date(2025, 5, 15).getTime()
    expect(formatDate(ts)).toBe('2025-06-15')
  })

  it('formats ISO string', () => {
    expect(formatDate('2025-03-01T12:00:00Z')).toMatch(/^2025-03-0[12]$/) // timezone dependent
  })

  it('pads single-digit month and day', () => {
    expect(formatDate(new Date(2025, 0, 1))).toBe('2025-01-01')
  })
})

describe('formatDateTime', () => {
  it('formats Date to YYYY-MM-DD HH:mm:ss', () => {
    const d = new Date(2025, 5, 15, 9, 5, 3)
    expect(formatDateTime(d)).toBe('2025-06-15 09:05:03')
  })

  it('pads hours, minutes, seconds', () => {
    const d = new Date(2025, 0, 1, 0, 0, 0)
    expect(formatDateTime(d)).toBe('2025-01-01 00:00:00')
  })
})

describe('formatTime', () => {
  it('formats Date to HH:mm', () => {
    const d = new Date(2025, 0, 1, 14, 30)
    expect(formatTime(d)).toBe('14:30')
  })

  it('pads single-digit hours and minutes', () => {
    const d = new Date(2025, 0, 1, 8, 5)
    expect(formatTime(d)).toBe('08:05')
  })
})

describe('formatRelativeTime', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns empty string for falsy input', () => {
    expect(formatRelativeTime('')).toBe('')
    expect(formatRelativeTime(0)).toBe('')
  })

  it('returns "刚刚" for less than 1 minute ago', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 0, 1, 12, 0, 30))
    expect(formatRelativeTime(new Date(2025, 0, 1, 12, 0, 0))).toBe('刚刚')
  })

  it('returns minutes for < 60 minutes ago', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 0, 1, 12, 10, 0))
    expect(formatRelativeTime(new Date(2025, 0, 1, 12, 0, 0))).toBe('10 分钟前')
  })

  it('returns hours for < 24 hours ago', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 0, 1, 15, 0, 0))
    expect(formatRelativeTime(new Date(2025, 0, 1, 12, 0, 0))).toBe('3 小时前')
  })

  it('returns days for < 30 days ago', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 0, 8, 12, 0, 0))
    expect(formatRelativeTime(new Date(2025, 0, 1, 12, 0, 0))).toBe('7 天前')
  })

  it('returns formatted date for >= 30 days ago', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 3, 1, 12, 0, 0))
    const result = formatRelativeTime(new Date(2025, 0, 1, 12, 0, 0))
    // toLocaleDateString('zh-CN') format
    expect(result).toBeTruthy()
    expect(result).not.toContain('天前')
  })

  it('accepts timestamp number input', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 0, 1, 12, 5, 0))
    const ts = new Date(2025, 0, 1, 12, 0, 0).getTime()
    expect(formatRelativeTime(ts)).toBe('5 分钟前')
  })

  it('accepts ISO string input', () => {
    vi.useFakeTimers()
    const now = new Date(2025, 0, 1, 12, 30, 0)
    vi.setSystemTime(now)
    const str = new Date(2025, 0, 1, 12, 0, 0).toISOString()
    expect(formatRelativeTime(str)).toBe('30 分钟前')
  })
})
