import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ELoginLayout from '@/components/login-layout/ELoginLayout.vue'

describe('ELoginLayout', () => {
  it('renders with default props', () => {
    const wrapper = mount(ELoginLayout)
    expect(wrapper.find('[data-slot="login-layout"]').exists()).toBe(true)
  })

  it('renders title prop', () => {
    const wrapper = mount(ELoginLayout, {
      props: { title: 'Welcome Back' },
    })
    expect(wrapper.find('h1').text()).toBe('Welcome Back')
  })

  it('renders slot content (form area)', () => {
    const wrapper = mount(ELoginLayout, {
      slots: { default: '<form class="login-form">Login Form</form>' },
    })
    expect(wrapper.find('.login-form').exists()).toBe(true)
    expect(wrapper.text()).toContain('Login Form')
  })

  it('renders logo when logo prop is provided', () => {
    const wrapper = mount(ELoginLayout, {
      props: { logo: '/logo.png' },
    })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('/logo.png')
  })

  it('does not render title when title prop is empty', () => {
    const wrapper = mount(ELoginLayout)
    expect(wrapper.find('h1').exists()).toBe(false)
  })

  it('applies background style when background prop is provided', () => {
    const wrapper = mount(ELoginLayout, {
      props: { background: 'linear-gradient(135deg, #667eea, #764ba2)' },
    })
    const el = wrapper.find('[data-slot="login-layout"]')
    expect(el.attributes('style')).toContain('linear-gradient')
  })

  it('renders footer slot when provided', () => {
    const wrapper = mount(ELoginLayout, {
      slots: { footer: '<span class="footer-text">Footer Info</span>' },
    })
    expect(wrapper.find('.footer-text').text()).toBe('Footer Info')
  })
})
