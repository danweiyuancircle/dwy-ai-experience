import { flushPromises, mount } from '@vue/test-utils'
import { h } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import EForm from '@/components/form/EForm.vue'
import EFormItem from '@/components/form/EFormItem.vue'
import ESwitch from '@/components/switch/ESwitch.vue'
import ESelect from '@/components/select/ESelect.vue'
import ENumberField from '@/components/number-field/ENumberField.vue'
import EDatePicker from '@/components/date-picker/EDatePicker.vue'

const fields = [
  { name: 'switch', component: ESwitch, props: { modelValue: false }, selector: 'button[role="switch"]' },
  { name: 'single select', component: ESelect, props: { options: [{ label: '选项', value: 'option' }] }, selector: 'button[role="combobox"]' },
  { name: 'multiple select', component: ESelect, props: { multiple: true, modelValue: [], options: [{ label: '选项', value: 'option' }] }, selector: 'button[role="combobox"]' },
  { name: 'number default', component: ENumberField, props: { modelValue: 0 }, selector: 'input[role="spinbutton"]' },
  { name: 'number right', component: ENumberField, props: { modelValue: 0, controlsPosition: 'right' }, selector: 'input[role="spinbutton"]' },
  ...['date', 'daterange', 'month', 'year'].map(type => ({
    name: `${type} picker`, component: EDatePicker, props: { type }, selector: 'button',
  })),
]

describe('EFormItem interactive control association', () => {
  it.each([false, true])('date dialog keeps its name linked to the real trigger, inside form: %s', async (insideForm) => {
    vi.stubGlobal('ResizeObserver', class {
      observe() {}
      unobserve() {}
      disconnect() {}
    })
    const wrapper = insideForm
      ? mount(EFormItem, {
          props: { label: '开始日期' },
          slots: { default: () => h(EDatePicker) },
          attachTo: document.body,
        })
      : mount(EDatePicker, { attachTo: document.body })
    try {
      const trigger = wrapper.get('button')
      await trigger.trigger('click')
      await flushPromises()
      const dialog = document.body.querySelector('[role="dialog"]')
      expect(dialog).not.toBeNull()
      expect(dialog?.getAttribute('aria-labelledby')).toBe(trigger.attributes('id'))
      expect(document.getElementById(dialog!.getAttribute('aria-labelledby')!)).toBe(trigger.element)
    } finally {
      wrapper.unmount()
      vi.unstubAllGlobals()
    }
  })

  it.each(fields)('$name has unique input ids, a functional label and validation description', async ({ component, props, selector }) => {
    const wrapper = mount(EForm, {
      props: {
        model: { first: '', second: '' },
        rules: {
          first: { validator: () => new Error('第一个字段无效') },
          second: { validator: () => new Error('第二个字段无效') },
        },
      },
      slots: {
        default: () => ['first', 'second'].map((prop, index) =>
          h(EFormItem, { prop, label: `字段 ${index + 1}` }, { default: () => h(component, props) }),
        ),
      },
    })
    try {
      const items = wrapper.findAll('[data-slot="form-item"]')
      for (const item of items) {
        const input = item.get(selector)
        const label = item.get('label')
        expect(label.element.control).toBe(input.element)
        expect(input.attributes('id')).toBe(label.attributes('for'))
        expect(input.attributes('aria-describedby')).toBeUndefined()
      }
      const ids = wrapper.findAll('[id]').map(node => node.attributes('id'))
      expect(new Set(ids).size).toBe(ids.length)

      await (wrapper.vm as unknown as { validate: () => Promise<boolean> }).validate()
      await flushPromises()
      for (const item of items) {
        const input = item.get(selector)
        const message = item.get('[data-slot="form-message"]')
        expect(input.attributes('aria-invalid')).toBe('true')
        expect(input.attributes('aria-describedby')).toBe(message.attributes('id'))
        expect(item.get('label').element.control).toBe(input.element)
      }
      const validatedIds = wrapper.findAll('[id]').map(node => node.attributes('id'))
      expect(new Set(validatedIds).size).toBe(validatedIds.length)
      ;(wrapper.vm as unknown as { clearValidate: () => void }).clearValidate()
      await flushPromises()
      for (const item of items) {
        const input = item.get(selector)
        expect(input.attributes('aria-invalid')).toBeUndefined()
        expect(input.attributes('aria-describedby')).toBeUndefined()
        expect(item.find('[data-slot="form-message"]').exists()).toBe(false)
      }
    } finally { wrapper.unmount() }
  })
})
