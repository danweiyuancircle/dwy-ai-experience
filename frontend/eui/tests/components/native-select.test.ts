import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ENativeSelect from '@/components/native-select/ENativeSelect.vue'

describe('ENativeSelect', () => {
  it('renders a select element', () => {
    const wrapper = mount(ENativeSelect)
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('renders options from options prop', () => {
    const options = [
      { label: '选项一', value: '1' },
      { label: '选项二', value: '2' },
      { label: '选项三', value: '3' },
    ]
    const wrapper = mount(ENativeSelect, { props: { options } })
    const optionEls = wrapper.findAll('option')
    // options only (no placeholder)
    expect(optionEls).toHaveLength(3)
    expect(optionEls[0].text()).toBe('选项一')
    expect(optionEls[1].text()).toBe('选项二')
  })

  it('renders placeholder as disabled option', () => {
    const wrapper = mount(ENativeSelect, {
      props: {
        placeholder: '请选择',
        options: [{ label: 'A', value: 'a' }],
      },
    })
    const optionEls = wrapper.findAll('option')
    // placeholder + 1 option
    expect(optionEls).toHaveLength(2)
    expect(optionEls[0].text()).toBe('请选择')
    expect(optionEls[0].attributes('disabled')).toBeDefined()
  })

  it('applies disabled attribute to select', () => {
    const wrapper = mount(ENativeSelect, { props: { disabled: true } })
    expect(wrapper.find('select').attributes('disabled')).toBeDefined()
  })

  it('emits update:modelValue on change', async () => {
    const options = [
      { label: 'A', value: 'a' },
      { label: 'B', value: 'b' },
    ]
    const wrapper = mount(ENativeSelect, {
      props: { options, modelValue: 'a' },
    })
    await wrapper.find('select').setValue('b')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['b'])
  })

  it('has data-slot attribute on wrapper and select', () => {
    const wrapper = mount(ENativeSelect)
    expect(wrapper.find('[data-slot="native-select-wrapper"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="native-select"]').exists()).toBe(true)
  })
})
