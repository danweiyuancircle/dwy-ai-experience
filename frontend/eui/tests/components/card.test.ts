import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECard from '@/components/card/ECard.vue'

describe('ECard', () => {
  it('renders a card element with data-slot attribute', () => {
    const wrapper = mount(ECard)
    expect(wrapper.find('[data-slot="card"]').exists()).toBe(true)
  })

  it('applies default card classes', () => {
    const wrapper = mount(ECard)
    const card = wrapper.find('[data-slot="card"]')
    expect(card.classes()).toContain('bg-card')
    expect(card.classes()).toContain('rounded-xl')
    expect(card.classes()).toContain('border')
  })

  it('renders title when title prop is provided', () => {
    const wrapper = mount(ECard, { props: { title: '卡片标题' } })
    const title = wrapper.find('[data-slot="card-title"]')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('卡片标题')
  })

  it('renders description when description prop is provided', () => {
    const wrapper = mount(ECard, { props: { title: '标题', description: '卡片描述' } })
    const desc = wrapper.find('[data-slot="card-description"]')
    expect(desc.exists()).toBe(true)
    expect(desc.text()).toBe('卡片描述')
  })

  it('renders default slot content', () => {
    const wrapper = mount(ECard, { slots: { default: '<p>卡片内容</p>' } })
    const content = wrapper.find('[data-slot="card-content"]')
    expect(content.exists()).toBe(true)
    expect(content.text()).toBe('卡片内容')
  })

  it('does not render card-content when default slot is empty', () => {
    const wrapper = mount(ECard)
    expect(wrapper.find('[data-slot="card-content"]').exists()).toBe(false)
  })

  it('renders header slot and overrides title/description', () => {
    const wrapper = mount(ECard, {
      props: { title: '被覆盖的标题' },
      slots: { header: '<div class="custom-header">自定义头部</div>' },
    })
    expect(wrapper.find('.custom-header').exists()).toBe(true)
    expect(wrapper.find('[data-slot="card-header"]').exists()).toBe(false)
  })

  it('renders footer slot content', () => {
    const wrapper = mount(ECard, {
      slots: { footer: '<button>操作按钮</button>' },
    })
    const footer = wrapper.find('[data-slot="card-footer"]')
    expect(footer.exists()).toBe(true)
    expect(footer.text()).toBe('操作按钮')
  })

  it('does not render footer when footer slot is empty', () => {
    const wrapper = mount(ECard)
    expect(wrapper.find('[data-slot="card-footer"]').exists()).toBe(false)
  })

  it('merges custom class with default classes', () => {
    const wrapper = mount(ECard, { props: { class: 'my-custom-class' } })
    const card = wrapper.find('[data-slot="card"]')
    expect(card.classes()).toContain('my-custom-class')
    expect(card.classes()).toContain('bg-card')
  })

  it('renders action slot inside header', () => {
    const wrapper = mount(ECard, {
      props: { title: '标题' },
      slots: { action: '<button>Action</button>' },
    })
    const action = wrapper.find('[data-slot="card-action"]')
    expect(action.exists()).toBe(true)
    expect(action.text()).toBe('Action')
  })
})
