import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAvatar from '@/components/avatar/EAvatar.vue'

describe('EAvatar', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EAvatar)
    expect(wrapper.attributes('data-slot')).toBe('avatar')
  })

  it('renders img when src is provided', () => {
    const wrapper = mount(EAvatar, {
      props: { src: 'https://example.com/avatar.jpg' },
    })
    const img = wrapper.find('[data-slot="avatar-image"]')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/avatar.jpg')
  })

  it('renders alt attribute on img', () => {
    const wrapper = mount(EAvatar, {
      props: { src: 'https://example.com/avatar.jpg', alt: 'User Avatar' },
    })
    const img = wrapper.find('[data-slot="avatar-image"]')
    expect(img.attributes('alt')).toBe('User Avatar')
  })

  it('renders fallback text when no src is provided', () => {
    const wrapper = mount(EAvatar, {
      props: { fallback: 'AB' },
    })
    const fallback = wrapper.find('[data-slot="avatar-fallback"]')
    expect(fallback.exists()).toBe(true)
    expect(fallback.text()).toBe('AB')
  })

  it('renders slot content as fallback', () => {
    const wrapper = mount(EAvatar, {
      slots: { default: '<span class="icon">U</span>' },
    })
    const fallback = wrapper.find('[data-slot="avatar-fallback"]')
    expect(fallback.find('.icon').exists()).toBe(true)
    expect(fallback.find('.icon').text()).toBe('U')
  })

  it('applies default size class (size-10)', () => {
    const wrapper = mount(EAvatar)
    expect(wrapper.classes()).toContain('size-10')
  })

  it('applies sm size class (size-8)', () => {
    const wrapper = mount(EAvatar, {
      props: { size: 'sm' },
    })
    expect(wrapper.classes()).toContain('size-8')
  })

  it('applies lg size class (size-12)', () => {
    const wrapper = mount(EAvatar, {
      props: { size: 'lg' },
    })
    expect(wrapper.classes()).toContain('size-12')
  })

  it('merges custom class', () => {
    const wrapper = mount(EAvatar, {
      props: { class: 'my-avatar' },
    })
    expect(wrapper.classes()).toContain('my-avatar')
  })
})
