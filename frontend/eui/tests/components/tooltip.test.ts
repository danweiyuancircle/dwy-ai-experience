import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETooltip from '@/components/tooltip/ETooltip.vue'

describe('ETooltip', () => {
  it('mounts without error', () => {
    const wrapper = mount(ETooltip, {
      slots: { default: '<button>Hover me</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the trigger slot with data-slot attribute', () => {
    const wrapper = mount(ETooltip, {
      slots: { default: '<span>Trigger</span>' },
    })
    const trigger = wrapper.find('[data-slot="tooltip-trigger"]')
    expect(trigger.exists()).toBe(true)
    expect(trigger.text()).toContain('Trigger')
  })

  it('trigger has data-state="closed" initially', () => {
    const wrapper = mount(ETooltip, {
      slots: { default: '<button>Hover</button>' },
    })
    const trigger = wrapper.find('[data-slot="tooltip-trigger"]')
    expect(trigger.attributes('data-state')).toBe('closed')
  })

  it('does not render tooltip content in closed state (portaled)', () => {
    const wrapper = mount(ETooltip, {
      props: { content: 'Tooltip text' },
      slots: { default: '<button>Hover</button>' },
    })
    expect(wrapper.find('[data-slot="tooltip-content"]').exists()).toBe(false)
  })

  it('accepts content prop without error', () => {
    const wrapper = mount(ETooltip, {
      props: { content: 'Hello tooltip' },
      slots: { default: '<button>Hover</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop without error', () => {
    const wrapper = mount(ETooltip, {
      props: { side: 'top', content: 'Top tooltip' },
      slots: { default: '<button>Hover</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts disabled prop', () => {
    const wrapper = mount(ETooltip, {
      props: { disabled: true, content: 'Disabled tooltip' },
      slots: { default: '<button>Hover</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts delayDuration prop', () => {
    const wrapper = mount(ETooltip, {
      props: { delayDuration: 500, content: 'Delayed' },
      slots: { default: '<button>Hover</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('click trigger opens content on pointer', async () => {
    document.body.innerHTML = ''
    const wrapper = mount(ETooltip, {
      attachTo: document.body,
      props: { content: 'Click tip', trigger: 'click' },
      slots: { default: '<button type="button">Open</button>' },
    })
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(document.body.textContent).toContain('Click tip')
    wrapper.unmount()
  })
})

