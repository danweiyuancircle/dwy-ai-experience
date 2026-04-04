import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import EWatermark from '@/components/watermark/EWatermark.vue'

// Mock canvas getContext since jsdom does not support it
beforeEach(() => {
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
    font: '',
    globalAlpha: 1,
    fillStyle: '',
    textAlign: '',
    textBaseline: '',
    measureText: vi.fn().mockReturnValue({ width: 100 }),
    translate: vi.fn(),
    rotate: vi.fn(),
    fillText: vi.fn(),
  }) as unknown as typeof HTMLCanvasElement.prototype.getContext

  HTMLCanvasElement.prototype.toDataURL = vi.fn().mockReturnValue('data:image/png;base64,mock')
})

describe('EWatermark', () => {
  it('renders a container element', () => {
    const wrapper = mount(EWatermark)
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EWatermark, {
      slots: { default: '<p>Protected content</p>' },
    })
    expect(wrapper.text()).toContain('Protected content')
  })

  it('accepts custom content prop', () => {
    const wrapper = mount(EWatermark, {
      props: { content: 'Confidential' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts array content prop', () => {
    const wrapper = mount(EWatermark, {
      props: { content: ['Line 1', 'Line 2'] },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('applies watermark background overlay', async () => {
    const wrapper = mount(EWatermark, {
      props: { content: 'Test' },
    })
    // Wait for onMounted to execute canvas drawing
    await new Promise((resolve) => setTimeout(resolve, 50))
    const overlayDivs = wrapper.findAll('div')
    // Should have at least the container and the watermark overlay div
    expect(overlayDivs.length).toBeGreaterThanOrEqual(2)
  })
})
