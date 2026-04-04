import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import { defineComponent, inject } from 'vue'
import EConfigProvider from '@/components/config-provider/EConfigProvider.vue'
import { CONFIG_PROVIDER_KEY } from '@/composables/useConfigProvider'

// Helper component to consume the provided context
const Consumer = defineComponent({
  setup() {
    const config = inject(CONFIG_PROVIDER_KEY)
    return { config }
  },
  template: '<div class="consumer">{{ config?.size }} {{ config?.zIndex }}</div>',
})

describe('EConfigProvider', () => {
  it('renders slot content', () => {
    const wrapper = mount(EConfigProvider, {
      slots: { default: '<span class="child">Hello</span>' },
    })
    expect(wrapper.find('.child').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello')
  })

  it('provides default size and zIndex', () => {
    const wrapper = mount(EConfigProvider, {
      slots: { default: () => [mount(Consumer).vm.$el] },
    })

    // Mount with consumer to verify injection
    const combined = mount(defineComponent({
      components: { EConfigProvider, Consumer },
      template: '<EConfigProvider><Consumer /></EConfigProvider>',
    }))
    expect(combined.find('.consumer').text()).toContain('default')
    expect(combined.find('.consumer').text()).toContain('2000')
  })

  it('provides custom size prop', () => {
    const combined = mount(defineComponent({
      components: { EConfigProvider, Consumer },
      template: '<EConfigProvider size="small"><Consumer /></EConfigProvider>',
    }))
    expect(combined.find('.consumer').text()).toContain('small')
  })

  it('provides custom zIndex prop', () => {
    const combined = mount(defineComponent({
      components: { EConfigProvider, Consumer },
      template: '<EConfigProvider :z-index="3000"><Consumer /></EConfigProvider>',
    }))
    expect(combined.find('.consumer').text()).toContain('3000')
  })
})
