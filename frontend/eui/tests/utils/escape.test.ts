import { describe, it, expect } from 'vitest'
import { escapeHtml } from '@/utils/escape'

describe('escapeHtml', () => {
  it('escapes & to &amp;', () => {
    expect(escapeHtml('a & b')).toBe('a &amp; b')
  })

  it('escapes < and > to &lt; and &gt;', () => {
    expect(escapeHtml('<script>alert(1)</script>')).toBe('&lt;script&gt;alert(1)&lt;/script&gt;')
  })

  it('escapes " to &quot;', () => {
    expect(escapeHtml('a "b" c')).toBe('a &quot;b&quot; c')
  })

  it("escapes ' to &#039;", () => {
    expect(escapeHtml("a 'b' c")).toBe('a &#039;b&#039; c')
  })

  it('escapes all special characters together', () => {
    expect(escapeHtml('<img src="x" onerror=\'alert(1)\'>')).toBe(
      '&lt;img src=&quot;x&quot; onerror=&#039;alert(1)&#039;&gt;',
    )
  })

  it('returns the same string when no special characters', () => {
    expect(escapeHtml('hello world 123')).toBe('hello world 123')
  })

  it('handles empty string', () => {
    expect(escapeHtml('')).toBe('')
  })
})
