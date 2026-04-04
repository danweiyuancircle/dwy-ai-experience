import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EBreadcrumb from '@/components/breadcrumb/EBreadcrumb.vue'

describe('EBreadcrumb', () => {
  it('renders nav element with correct attributes', () => {
    const wrapper = mount(EBreadcrumb)
    expect(wrapper.element.tagName).toBe('NAV')
    expect(wrapper.attributes('aria-label')).toBe('breadcrumb')
    expect(wrapper.attributes('data-slot')).toBe('breadcrumb')
  })

  it('renders breadcrumb items', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        items: [
          { label: 'Home', href: '/' },
          { label: 'Products', href: '/products' },
          { label: 'Detail' },
        ],
      },
    })
    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('Products')
    expect(wrapper.text()).toContain('Detail')
  })

  it('renders last item as current page', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        items: [
          { label: 'Home', href: '/' },
          { label: 'Current' },
        ],
      },
    })
    const page = wrapper.find('[data-slot="breadcrumb-page"]')
    expect(page.exists()).toBe(true)
    expect(page.attributes('aria-current')).toBe('page')
    expect(page.attributes('aria-disabled')).toBe('true')
    expect(page.text()).toBe('Current')
  })

  it('renders non-last items with href as links', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        items: [
          { label: 'Home', href: '/' },
          { label: 'Products', href: '/products' },
          { label: 'Detail' },
        ],
      },
    })
    const links = wrapper.findAll('a[data-slot="breadcrumb-link"]')
    expect(links).toHaveLength(2)
    expect(links[0].attributes('href')).toBe('/')
    expect(links[0].text()).toBe('Home')
    expect(links[1].attributes('href')).toBe('/products')
    expect(links[1].text()).toBe('Products')
  })

  it('renders non-last items without href as span', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        items: [
          { label: 'Category' },
          { label: 'Detail' },
        ],
      },
    })
    const links = wrapper.findAll('a[data-slot="breadcrumb-link"]')
    expect(links).toHaveLength(0)
    const spanLinks = wrapper.findAll('span[data-slot="breadcrumb-link"]')
    expect(spanLinks).toHaveLength(1)
    expect(spanLinks[0].text()).toBe('Category')
  })

  it('renders separators between items', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        items: [
          { label: 'A', href: '/' },
          { label: 'B', href: '/b' },
          { label: 'C' },
        ],
      },
    })
    const separators = wrapper.findAll('[data-slot="breadcrumb-separator"]')
    expect(separators).toHaveLength(2)
  })

  it('renders custom text separator', () => {
    const wrapper = mount(EBreadcrumb, {
      props: {
        separator: '/',
        items: [
          { label: 'A', href: '/' },
          { label: 'B' },
        ],
      },
    })
    const separator = wrapper.find('[data-slot="breadcrumb-separator"]')
    expect(separator.text()).toBe('/')
  })

  it('renders empty list without errors', () => {
    const wrapper = mount(EBreadcrumb, { props: { items: [] } })
    const items = wrapper.findAll('[data-slot="breadcrumb-item"]')
    expect(items).toHaveLength(0)
  })

  it('merges custom class on nav', () => {
    const wrapper = mount(EBreadcrumb, { props: { class: 'my-nav' } })
    expect(wrapper.classes()).toContain('my-nav')
  })
})
