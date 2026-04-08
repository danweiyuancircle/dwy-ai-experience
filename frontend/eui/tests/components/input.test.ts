import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EInput from '@/components/input/EInput.vue'

describe('EInput', () => {
  it('renders an input element', () => {
    const wrapper = mount(EInput)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('renders with placeholder', () => {
    const wrapper = mount(EInput, { props: { placeholder: '请输入' } })
    expect(wrapper.find('input').attributes('placeholder')).toBe('请输入')
  })

  it('uses text type by default', () => {
    const wrapper = mount(EInput)
    expect(wrapper.find('input').attributes('type')).toBe('text')
  })

  it('applies disabled attribute', () => {
    const wrapper = mount(EInput, { props: { disabled: true } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('applies readonly attribute', () => {
    const wrapper = mount(EInput, { props: { readonly: true } })
    expect(wrapper.find('input').attributes('readonly')).toBeDefined()
  })

  it('applies sm size class', () => {
    const wrapper = mount(EInput, { props: { size: 'sm' } })
    expect(wrapper.find('input').classes()).toContain('h-8')
  })

  it('applies lg size class', () => {
    const wrapper = mount(EInput, { props: { size: 'lg' } })
    expect(wrapper.find('input').classes()).toContain('h-10')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(EInput)
    const input = wrapper.find('input')
    // Simulate setting value and triggering input event
    await input.setValue('hello')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['hello'])
  })

  it('emits blur event', async () => {
    const wrapper = mount(EInput)
    await wrapper.find('input').trigger('blur')
    expect(wrapper.emitted('blur')).toHaveLength(1)
  })

  it('emits focus event', async () => {
    const wrapper = mount(EInput)
    await wrapper.find('input').trigger('focus')
    expect(wrapper.emitted('focus')).toHaveLength(1)
  })

  it('shows clear button when clearable and has value', () => {
    const wrapper = mount(EInput, {
      props: { clearable: true, modelValue: 'text' },
    })
    // Clear button should exist (the X icon button)
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('hides clear button when value is empty', () => {
    const wrapper = mount(EInput, {
      props: { clearable: true, modelValue: '' },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(0)
  })

  it('emits clear and update:modelValue on clear click', async () => {
    const wrapper = mount(EInput, {
      props: { clearable: true, modelValue: 'text' },
    })
    const button = wrapper.find('button')
    await button.trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([''])
    expect(wrapper.emitted('clear')).toHaveLength(1)
  })

  it('shows password toggle when showPassword is true', () => {
    const wrapper = mount(EInput, {
      props: { showPassword: true, modelValue: 'secret' },
    })
    expect(wrapper.find('input').attributes('type')).toBe('password')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('toggles password visibility on button click', async () => {
    const wrapper = mount(EInput, {
      props: { showPassword: true, modelValue: 'secret' },
    })
    const input = wrapper.find('input')
    expect(input.attributes('type')).toBe('password')

    await wrapper.find('button').trigger('click')
    expect(input.attributes('type')).toBe('text')

    await wrapper.find('button').trigger('click')
    expect(input.attributes('type')).toBe('password')
  })

  it('applies maxlength attribute', () => {
    const wrapper = mount(EInput, { props: { maxlength: 10 } })
    expect(wrapper.find('input').attributes('maxlength')).toBe('10')
  })

  it('has data-slot attribute on wrapper', () => {
    const wrapper = mount(EInput)
    expect(wrapper.attributes('data-slot')).toBe('input-root')
  })

  // autocomplete prop
  it('passes autocomplete attribute to input', () => {
    const wrapper = mount(EInput, { props: { autocomplete: 'username' } })
    expect(wrapper.find('input').attributes('autocomplete')).toBe('username')
  })

  it('does not set autocomplete by default', () => {
    const wrapper = mount(EInput, { props: { type: 'password' } })
    expect(wrapper.find('input').attributes('autocomplete')).toBeUndefined()
  })

  // name prop
  it('passes name attribute to input', () => {
    const wrapper = mount(EInput, { props: { name: 'username' } })
    expect(wrapper.find('input').attributes('name')).toBe('username')
  })

  it('sets spellcheck="false" for password type', () => {
    const wrapper = mount(EInput, { props: { type: 'password' } })
    expect(wrapper.find('input').attributes('spellcheck')).toBe('false')
  })

  it('sets autocorrect="off" for password type', () => {
    const wrapper = mount(EInput, { props: { type: 'password' } })
    expect(wrapper.find('input').attributes('autocorrect')).toBe('off')
  })

  it('does not set autocomplete for text type', () => {
    const wrapper = mount(EInput, { props: { type: 'text' } })
    expect(wrapper.find('input').attributes('autocomplete')).toBeUndefined()
  })

  // Security: DOM value hiding (secure value)
  it('does not expose value as HTML attribute', async () => {
    const wrapper = mount(EInput, { props: { modelValue: 'secret' } })
    const input = wrapper.find('input')
    // HTML attribute should not contain the value
    expect(input.attributes('value')).toBeUndefined()
    // DOM property should have the value
    expect((input.element as HTMLInputElement).value).toBe('secret')
  })

  it('updates DOM property without HTML attribute on modelValue change', async () => {
    const wrapper = mount(EInput, { props: { modelValue: '' } })
    await wrapper.setProps({ modelValue: 'updated' })
    const input = wrapper.find('input')
    expect(input.attributes('value')).toBeUndefined()
    expect((input.element as HTMLInputElement).value).toBe('updated')
  })
})
