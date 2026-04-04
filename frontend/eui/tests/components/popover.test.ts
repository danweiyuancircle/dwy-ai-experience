import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EPopover from '@/components/popover/EPopover.vue'

describe('EPopover', () => {
  it('mounts without error', () => {
    const wrapper = mount(EPopover, {
      slots: { trigger: '<button>Open</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the trigger slot with data-slot attribute', () => {
    const wrapper = mount(EPopover, {
      slots: { trigger: '<button>Click me</button>' },
    })
    const trigger = wrapper.find('[data-slot="popover-trigger"]')
    expect(trigger.exists()).toBe(true)
    expect(trigger.text()).toContain('Click me')
  })

  it('trigger has data-state="closed" initially', () => {
    const wrapper = mount(EPopover, {
      slots: { trigger: '<button>Open</button>' },
    })
    const trigger = wrapper.find('[data-slot="popover-trigger"]')
    expect(trigger.attributes('data-state')).toBe('closed')
  })

  it('does not render popover content in closed state (portaled)', () => {
    const wrapper = mount(EPopover, {
      slots: {
        trigger: '<button>Open</button>',
        default: 'Popover body',
      },
    })
    expect(wrapper.find('[data-slot="popover-content"]').exists()).toBe(false)
  })

  it('accepts open prop without error', () => {
    const wrapper = mount(EPopover, {
      props: { open: false },
      slots: { trigger: '<button>Open</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop without error', () => {
    const wrapper = mount(EPopover, {
      props: { side: 'bottom' },
      slots: { trigger: '<button>Open</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts align and sideOffset props without error', () => {
    const wrapper = mount(EPopover, {
      props: { align: 'start', sideOffset: 8 },
      slots: { trigger: '<button>Open</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })
})
