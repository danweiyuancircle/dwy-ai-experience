/**
 * RecordCode：等宽单号，空值用破折号。
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordCode } from '../../../src/components'

describe('RecordCode', () => {
  it('有单号时等宽显示，空值用淡色破折号', () => {
    const filled = mount(RecordCode, { props: { text: 'P001' } })
    const blank = mount(RecordCode, { props: { text: '' } })

    expect(filled.text()).toBe('P001')
    expect(filled.classes()).toContain('font-mono')
    expect(filled.classes()).not.toContain('text-muted-foreground')
    expect(blank.text()).toBe('—')
    expect(blank.classes()).toContain('text-muted-foreground')
  })
})
