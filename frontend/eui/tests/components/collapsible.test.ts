import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECollapsible from '@/components/collapsible/ECollapsible.vue'

describe('ECollapsible', () => {
  it('renders a collapsible root element', () => {
    const wrapper = mount(ECollapsible)
    expect(wrapper.find('[data-slot="collapsible"]').exists()).toBe(true)
  })

  it('renders trigger slot content', () => {
    const wrapper = mount(ECollapsible, {
      slots: {
        trigger: '<button>Toggle</button>',
        default: '<div>Content</div>',
      },
    })
    expect(wrapper.text()).toContain('Toggle')
  })

  it('renders default slot content', () => {
    const wrapper = mount(ECollapsible, {
      props: { modelValue: true },
      slots: {
        trigger: '<button>Toggle</button>',
        default: '<div>Collapsible Content</div>',
      },
    })
    expect(wrapper.text()).toContain('Collapsible Content')
  })

  it('emits update:modelValue when toggled', async () => {
    const wrapper = mount(ECollapsible, {
      props: { modelValue: false },
      slots: {
        trigger: '<button class="trigger-btn">Toggle</button>',
        default: '<div>Content</div>',
      },
    })
    const triggerBtn = wrapper.find('.trigger-btn')
    await triggerBtn.trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('applies disabled state', () => {
    const wrapper = mount(ECollapsible, {
      props: { disabled: true },
      slots: {
        trigger: '<button>Toggle</button>',
        default: '<div>Content</div>',
      },
    })
    const root = wrapper.find('[data-slot="collapsible"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('applies custom class to root', () => {
    const wrapper = mount(ECollapsible, {
      props: { class: 'custom-collapsible' },
    })
    const root = wrapper.find('[data-slot="collapsible"]')
    expect(root.classes()).toContain('custom-collapsible')
  })
})
