import { flushPromises, mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EInput from '@/components/input/EInput.vue'
import EConfigProvider from '@/components/config-provider/EConfigProvider.vue'

describe('EInput', () => {
  it('forwards native attributes and keyboard listeners to input, retaining root styles', async () => {
    let enterCount = 0
    const wrapper = mount(EInput, {
      props: { class: 'search-width' },
      attrs: {
        id: 'user-search', 'aria-label': '用户搜索', 'aria-labelledby': 'search-title',
        'aria-describedby': 'search-help', inputmode: 'search', required: true,
        style: { width: '240px' },
        onKeydown: (event: KeyboardEvent) => { if (event.key === 'Enter') enterCount++ },
      },
    })
    const input = wrapper.get('input')
    expect(input.attributes()).toMatchObject({
      id: 'user-search', 'aria-label': '用户搜索', 'aria-labelledby': 'search-title',
      'aria-describedby': 'search-help', inputmode: 'search', required: '',
    })
    expect(wrapper.classes()).toContain('search-width')
    expect(wrapper.attributes('style')).toContain('width: 240px')
    expect(wrapper.attributes('aria-label')).toBeUndefined()
    expect(wrapper.attributes('id')).toBeUndefined()
    await input.trigger('keydown', { key: 'Enter' })
    expect(enterCount).toBe(1)
    await wrapper.setProps({ 'aria-label': '更新后的搜索' })
    expect(input.attributes('aria-label')).toBe('更新后的搜索')
  })

  it('preserves explicit text correction attributes and valid falsy native values', async () => {
    const wrapper = mount(EInput, {
      attrs: { spellcheck: false, autocorrect: 'on', tabindex: 0 },
    })
    const input = wrapper.get('input')
    expect(input.attributes('spellcheck')).toBe('false')
    expect(input.attributes('autocorrect')).toBe('on')
    expect(input.element.tabIndex).toBe(0)
    await wrapper.setProps({ spellcheck: '', autocorrect: '' })
    expect(input.attributes('spellcheck')).toBe('')
    expect(input.attributes('autocorrect')).toBe('')
    await wrapper.setProps({ spellcheck: true, autocorrect: 'off' })
    expect(input.attributes('spellcheck')).toBe('true')
    expect(input.attributes('autocorrect')).toBe('off')
  })

  it.each([
    { type: 'password' },
    { showPassword: true },
  ])('password input overrides correction attributes even when visibility changes: %o', async (props) => {
    const wrapper = mount(EInput, {
      props,
      attrs: { spellcheck: true, autocorrect: 'on' },
    })
    const input = wrapper.get('input')
    expect(input.attributes('spellcheck')).toBe('false')
    expect(input.attributes('autocorrect')).toBe('off')
    if (props.showPassword) {
      await wrapper.get('button').trigger('click')
      expect(input.attributes('type')).toBe('text')
      expect(input.attributes('spellcheck')).toBe('false')
      expect(input.attributes('autocorrect')).toBe('off')
    }
    await wrapper.setProps(props.showPassword ? { showPassword: false } : { type: 'text' })
    expect(input.attributes('spellcheck')).toBe('true')
    expect(input.attributes('autocorrect')).toBe('on')
  })

  it('clear button has a keyboard-accessible name and returns focus to the input', async () => {
    const wrapper = mount(EInput, {
      attachTo: document.body,
      props: {
        clearable: true, modelValue: 'text',
        'onUpdate:modelValue': (value: string) => wrapper.setProps({ modelValue: value }),
      },
    })
    try {
      const button = wrapper.get('button')
      expect(button.attributes('aria-label')).toBe('清空输入')
      expect(button.element.tabIndex).toBe(0)
      button.element.focus()
      await button.trigger('click')
      await flushPromises()
      expect(wrapper.find('button').exists()).toBe(false)
      expect(document.activeElement).toBe(wrapper.get('input').element)
      expect(wrapper.get('input').element.value).toBe('')
      expect(wrapper.emitted('clear')).toHaveLength(1)
    } finally { wrapper.unmount() }
  })

  it('password toggle exposes its action, state and keyboard access', async () => {
    const wrapper = mount(EInput, { props: { showPassword: true, modelValue: 'secret' } })
    const button = wrapper.get('button')
    expect(button.attributes('aria-label')).toBe('显示密码')
    expect(button.attributes('aria-pressed')).toBe('false')
    expect(button.element.tabIndex).toBe(0)
    await button.trigger('click')
    expect(button.attributes('aria-label')).toBe('隐藏密码')
    expect(button.attributes('aria-pressed')).toBe('true')
    await wrapper.setProps({ disabled: true })
    expect(button.element.disabled).toBe(true)
    await button.trigger('click')
    expect(wrapper.get('input').attributes('type')).toBe('text')
  })

  it('input action names follow provider locale updates', async () => {
    const wrapper = mount(EConfigProvider, {
      props: { locale: { inputClear: 'Clear input', inputShowPassword: 'Show password', inputHidePassword: 'Hide password' } },
      slots: { default: '<div><EInput clearable model-value="query" /><EInput show-password /></div>' },
      global: { components: { EInput } },
    })
    expect(wrapper.findAll('button').map(button => button.attributes('aria-label'))).toEqual(['Clear input', 'Show password'])
    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.findAll('button')[1].attributes('aria-label')).toBe('Hide password')
    await wrapper.setProps({ locale: { inputClear: '清除查询' } })
    expect(wrapper.findAll('button')[0].attributes('aria-label')).toBe('清除查询')
  })

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

  it.each([
    ['email', 'user@example.com'],
    ['number', '42'],
    ['date', '2026-10-18'],
    ['month', '2026-10'],
    ['week', '2026-W42'],
    ['time', '12:30'],
    ['datetime-local', '2026-10-18T12:30'],
    ['range', '42'],
    ['color', '#123456'],
  ])('%s 原生输入保持类型和值，不对无选区控件恢复光标', async (type, value) => {
    const wrapper = mount(EInput, {
      props: {
        type,
        modelValue: '',
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val }),
      },
    })
    const input = wrapper.find('input')
    await input.setValue(value)
    // 排空 onInput 后的二次 nextTick，让非法 setSelectionRange 的异步异常暴露给 Vitest。
    await flushPromises()
    expect(input.element.type).toBe(type)
    expect(input.element.value).toBe(value)
    expect(wrapper.emitted('update:modelValue')).toEqual([[value]])
    expect(input.element.selectionStart).toBeNull()
    expect(input.element.selectionEnd).toBeNull()
    wrapper.unmount()
  })

  it('邮箱输入保留原生格式校验，不能用 text 规避选区限制', async () => {
    const wrapper = mount(EInput, {
      props: {
        type: 'email',
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val }),
      },
    })
    const input = wrapper.find('input')
    await input.setValue('invalid-email')
    await flushPromises()
    expect(input.element.type).toBe('email')
    expect(input.element.validity.typeMismatch).toBe(true)
    expect(wrapper.emitted('update:modelValue')).toEqual([['invalid-email']])
    wrapper.unmount()
  })

  it.each(['text', 'search', 'tel', 'url', 'password'])('%s 输入在父层规范化值后恢复选区', async (type) => {
    const wrapper = mount(EInput, {
      props: {
        type,
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val.toUpperCase() }),
      },
    })
    const input = wrapper.find('input')
    input.element.value = 'abcde'
    input.element.setSelectionRange(1, 3)
    await input.trigger('input')
    await flushPromises()
    expect(input.element.value).toBe('ABCDE')
    expect(input.element.selectionStart).toBe(1)
    expect(input.element.selectionEnd).toBe(3)
    wrapper.unmount()
  })

  it('父层在输入后切换成 email 时，按恢复时的类型跳过选区', async () => {
    const wrapper = mount(EInput, {
      props: {
        type: 'text',
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val, type: 'email' }),
      },
    })
    const input = wrapper.find('input')
    input.element.value = 'user@example.com'
    input.element.setSelectionRange(2, 2)
    await input.trigger('input')
    await flushPromises()
    expect(input.element.type).toBe('email')
    expect(input.element.value).toBe('user@example.com')
    expect(input.element.selectionStart).toBeNull()
    wrapper.unmount()
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

  it('root and wrapper can shrink inside a flex row', () => {
    const wrapper = mount(EInput)
    expect(wrapper.classes()).toContain('min-w-0')
    const inner = wrapper.find('[data-slot="input-wrapper"]')
    expect(inner.classes()).toContain('min-w-0')
  })
})
