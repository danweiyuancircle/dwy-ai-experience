import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EImage from '@/components/image/EImage.vue'

describe('EImage', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EImage)
    expect(wrapper.find('[data-slot="image"]').exists()).toBe(true)
  })

  it('renders img with src and alt props', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg', alt: 'A photo' },
    })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/photo.jpg')
    expect(img.attributes('alt')).toBe('A photo')
  })

  it('applies cover fit class by default', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg' },
    })
    const img = wrapper.find('img')
    expect(img.classes()).toContain('object-cover')
  })

  it('applies contain fit class', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg', fit: 'contain' },
    })
    const img = wrapper.find('img')
    expect(img.classes()).toContain('object-contain')
  })

  it('applies fill fit class', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg', fit: 'fill' },
    })
    const img = wrapper.find('img')
    expect(img.classes()).toContain('object-fill')
  })

  it('shows loading skeleton when image is not yet loaded', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg' },
    })
    // Before load event fires, the skeleton placeholder should be visible
    const skeleton = wrapper.find('.animate-pulse')
    expect(skeleton.exists()).toBe(true)
  })

  it('does not render img when src is not provided', () => {
    const wrapper = mount(EImage)
    const img = wrapper.find('img')
    expect(img.exists()).toBe(false)
  })

  it('renders img when lazy is false (default)', () => {
    const wrapper = mount(EImage, {
      props: { src: 'https://example.com/photo.jpg', lazy: false },
    })
    expect(wrapper.find('img').exists()).toBe(true)
  })

  it('merges custom class on container', () => {
    const wrapper = mount(EImage, {
      props: { class: 'w-64 h-48' },
    })
    const container = wrapper.find('[data-slot="image"]')
    expect(container.classes()).toContain('w-64')
    expect(container.classes()).toContain('h-48')
  })
})
