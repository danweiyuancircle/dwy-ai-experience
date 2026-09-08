import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { describe, it, expect } from 'vitest'
import { useFormField } from '@/composables/useFormField'
import EForm from '@/components/form/EForm.vue'
import EFormItem from '@/components/form/EFormItem.vue'
import EInput from '@/components/input/EInput.vue'

const Probe = defineComponent({
  setup() {
    const field = useFormField()
    return { inside: !!field, formItemId: field?.formItemId ?? '' }
  },
  template: '<span data-probe :data-inside="inside" :data-id="formItemId">ok</span>',
})

describe('useFormField', () => {
  it('表单外使用返回 null，不抛错', () => {
    const wrapper = mount(Probe)
    expect(wrapper.find('[data-probe]').attributes('data-inside')).toBe('false')
  })

  it('在 EFormItem 内能读到 formItem id', () => {
    const wrapper = mount(EForm, {
      props: { model: { name: '' } },
      slots: {
        default: () => h(EFormItem, { prop: 'name', label: '姓名' }, { default: () => h(Probe) }),
      },
    })
    const probe = wrapper.find('[data-probe]')
    expect(probe.attributes('data-inside')).toBe('true')
    expect(probe.attributes('data-id')).toContain('form-item')
  })

  it('EInput 在校验失败的 FormItem 内带 aria-invalid', async () => {
    const wrapper = mount(EForm, {
      props: {
        model: { name: '' },
        rules: { name: { required: true, message: '必填' } },
      },
      slots: {
        default: () => h(EFormItem, { prop: 'name', label: '姓名' }, {
          default: () => h(EInput, { modelValue: '' }),
        }),
      },
    })
    const form = wrapper.findComponent(EForm)
    await (form.vm as unknown as { validate: () => Promise<boolean> }).validate()
    await wrapper.vm.$nextTick()
    const input = wrapper.find('[data-slot="input"]')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('aria-describedby')).toContain('form-item-message')
  })
})
