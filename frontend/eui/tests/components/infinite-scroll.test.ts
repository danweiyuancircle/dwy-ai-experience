import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import EInfiniteScroll from '@/components/infinite-scroll/EInfiniteScroll.vue'

beforeAll(() => {
  // InfiniteScroll uses IntersectionObserver
  if (!globalThis.IntersectionObserver) {
    globalThis.IntersectionObserver = class {
      constructor(
        public callback: IntersectionObserverCallback,
        public options?: IntersectionObserverInit,
      ) {}
      observe() {}
      unobserve() {}
      disconnect() {}
      takeRecords(): IntersectionObserverEntry[] {
        return []
      }
      root = null
      rootMargin = ''
      thresholds = [0]
    } as unknown as typeof IntersectionObserver
  }
})

describe('EInfiniteScroll', () => {
  it('renders a root container element', () => {
    const wrapper = mount(EInfiniteScroll)
    expect(wrapper.find('.relative').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EInfiniteScroll, {
      slots: {
        default: '<div class="list-item">Item 1</div>',
      },
    })
    expect(wrapper.find('.list-item').exists()).toBe(true)
    expect(wrapper.text()).toContain('Item 1')
  })

  it('shows loading indicator when loading is true', () => {
    const wrapper = mount(EInfiniteScroll, {
      props: { loading: true },
    })
    // Default loading text
    expect(wrapper.text()).toContain('Loading...')
    // Should render the spinner icon
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('does not show loading indicator when loading is false', () => {
    const wrapper = mount(EInfiniteScroll, {
      props: { loading: false },
    })
    expect(wrapper.text()).not.toContain('Loading...')
  })

  it('shows complete message when disabled is true and not loading', () => {
    const wrapper = mount(EInfiniteScroll, {
      props: { disabled: true, loading: false },
    })
    expect(wrapper.text()).toContain('No more data')
  })

  it('renders custom loading slot content', () => {
    const wrapper = mount(EInfiniteScroll, {
      props: { loading: true },
      slots: {
        loading: 'Fetching more...',
      },
    })
    expect(wrapper.text()).toContain('Fetching more...')
  })

  it('renders custom complete slot content', () => {
    const wrapper = mount(EInfiniteScroll, {
      props: { disabled: true },
      slots: {
        complete: 'All done!',
      },
    })
    expect(wrapper.text()).toContain('All done!')
  })
})
