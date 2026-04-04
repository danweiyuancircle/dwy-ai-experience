import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import ECarousel from '@/components/carousel/ECarousel.vue'

// embla-carousel-vue uses internal DOM APIs that don't exist in jsdom.
// We mock the entire module so the component can mount without errors.
vi.mock('embla-carousel-vue', () => {
  const ref = (val: unknown) => ({ value: val })
  return {
    default: () => [ref(null), ref(undefined)],
  }
})

beforeAll(() => {
  if (!globalThis.ResizeObserver) {
    globalThis.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    } as unknown as typeof ResizeObserver
  }
})

describe('ECarousel', () => {
  it('renders a carousel root element', () => {
    const wrapper = mount(ECarousel)
    expect(wrapper.find('[data-slot="carousel"]').exists()).toBe(true)
  })

  it('has correct aria attributes', () => {
    const wrapper = mount(ECarousel)
    const root = wrapper.find('[data-slot="carousel"]')
    expect(root.attributes('role')).toBe('region')
    expect(root.attributes('aria-roledescription')).toBe('carousel')
  })

  it('renders slot content', () => {
    const wrapper = mount(ECarousel, {
      slots: {
        default: '<div class="slide-item">Slide 1</div>',
      },
    })
    expect(wrapper.find('.slide-item').exists()).toBe(true)
    expect(wrapper.text()).toContain('Slide 1')
  })

  it('renders arrow buttons when showArrows is true (default)', () => {
    const wrapper = mount(ECarousel)
    const prevBtn = wrapper.find('[aria-label="Previous slide"]')
    const nextBtn = wrapper.find('[aria-label="Next slide"]')
    expect(prevBtn.exists()).toBe(true)
    expect(nextBtn.exists()).toBe(true)
  })

  it('hides arrow buttons when showArrows is false', () => {
    const wrapper = mount(ECarousel, {
      props: { showArrows: false },
    })
    expect(wrapper.find('[aria-label="Previous slide"]').exists()).toBe(false)
    expect(wrapper.find('[aria-label="Next slide"]').exists()).toBe(false)
  })

  it('applies custom class to root element', () => {
    const wrapper = mount(ECarousel, {
      props: { class: 'my-carousel' },
    })
    const root = wrapper.find('[data-slot="carousel"]')
    expect(root.classes()).toContain('my-carousel')
  })
})
