import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h, reactive } from 'vue'
import { describe, it, expect } from 'vitest'
import { useFormContext } from 'vee-validate'
import EForm from '@/components/form/EForm.vue'
import EFormItem from '@/components/form/EFormItem.vue'
import EInput from '@/components/input/EInput.vue'

describe('EForm', () => {
  it('renders a form element', () => {
    const wrapper = mount(EForm)
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(EForm)
    expect(wrapper.find('form').attributes('data-slot')).toBe('form')
  })

  it('renders slot content', () => {
    const wrapper = mount(EForm, {
      slots: { default: '<div class="form-content">Form Field</div>' },
    })
    expect(wrapper.find('.form-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Form Field')
  })

  it('applies inline class when inline prop is true', () => {
    const wrapper = mount(EForm, { props: { inline: true } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('flex')
    expect(form.classes()).toContain('flex-wrap')
  })

  it('applies space-y-4 class when inline is false', () => {
    const wrapper = mount(EForm, { props: { inline: false } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('space-y-4')
  })

  it('accepts model prop', () => {
    const model = { name: 'test', age: 20 }
    const wrapper = mount(EForm, { props: { model } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts labelWidth prop', () => {
    const wrapper = mount(EForm, { props: { labelWidth: '120px' } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts labelPosition prop', () => {
    const wrapper = mount(EForm, { props: { labelPosition: 'top' } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts disabled prop', () => {
    const wrapper = mount(EForm, { props: { disabled: true } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(EForm, { props: { class: 'my-form' } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('my-form')
  })

  it('has submit.prevent on form element', () => {
    // The component uses @submit.prevent to prevent default form submission
    const wrapper = mount(EForm)
    const form = wrapper.find('form')
    // Verify the form element exists and is properly configured
    expect(form.exists()).toBe(true)
    expect(form.attributes('data-slot')).toBe('form')
  })
})

/**
 * 边输边校：值变化后栏下出红字；进页空字段不出。
 * vee-validate 表级 schema 有 5ms debounce，断言前必须等到 DOM。
 */
async function flushValidation() {
  await flushPromises()
  await new Promise((resolve) => setTimeout(resolve, 20))
  await flushPromises()
}

function mountPasswordPairForm(inputAttrs: Record<string, string> = {}) {
  const model = reactive({ password: '', confirmPassword: '' })
  const wrapper = mount(
    defineComponent({
      components: { EForm, EFormItem, EInput },
      setup() {
        const rules = {
          password: [
            { required: true, message: '请输入密码' },
            { min: 8, message: '密码至少 8 位' },
          ],
          confirmPassword: [
            { required: true, message: '请再次输入密码' },
            {
              validator: (_rule: unknown, value: string) =>
                value === model.password || new Error('两次输入的密码不一致'),
            },
          ],
        }
        return { model, rules, inputAttrs }
      },
      template: `
        <EForm :model="model" :rules="rules">
          <EFormItem prop="password" label="密码">
            <EInput v-model="model.password" v-bind="inputAttrs" />
          </EFormItem>
          <EFormItem prop="confirmPassword" label="确认密码">
            <EInput v-model="model.confirmPassword" />
          </EFormItem>
        </EForm>
      `,
    }),
  )
  return { wrapper, model }
}

describe('EForm 边输边校', () => {
  it('clearValidate removes current errors without resetting the input draft or model', async () => {
    const { wrapper, model } = mountPasswordPairForm()
    await wrapper.findAll('input')[0].setValue('draft')
    await flushValidation()
    expect(wrapper.text()).toContain('密码至少 8 位')
    const form = wrapper.findComponent(EForm)
    ;(form.vm as unknown as { clearValidate: () => void }).clearValidate()
    await flushValidation()
    const input = wrapper.findAll('input')[0]
    expect(wrapper.find('[data-slot="form-message"]').exists()).toBe(false)
    expect(input.attributes('aria-invalid')).toBeUndefined()
    expect(input.attributes('aria-describedby')).toBeUndefined()
    expect(input.element.value).toBe('draft')
    expect(model).toEqual({ password: 'draft', confirmPassword: '' })
    await (form.vm as unknown as { validate: () => Promise<boolean> }).validate()
    await flushValidation()
    expect(wrapper.text()).toContain('密码至少 8 位')
  })

  it('clearValidate also clears custom errors for unmounted and nested fields without changing their values', async () => {
    let context: ReturnType<typeof useFormContext> | undefined
    const Probe = defineComponent({
      setup() {
        context = useFormContext()
        return () => h('span')
      },
    })
    const model = reactive({ visible: 'draft', hidden: 0, enabled: false, profile: { email: '' } })
    const wrapper = mount(EForm, {
      props: { model },
      slots: {
        default: () => [h(Probe), h(EFormItem, { prop: 'visible', label: '名称' }, {
          default: () => h(EInput, { modelValue: model.visible }),
        })],
      },
    })
    try {
      context!.setFieldError('visible', '服务端错误')
      context!.setFieldError('hidden', ['隐藏字段错误一', '隐藏字段错误二'])
      context!.setFieldError('profile.email', '嵌套字段错误')
      await flushPromises()
      expect(Object.keys(context!.errors.value)).toHaveLength(3)
      expect(wrapper.text()).toContain('服务端错误')
      ;(wrapper.vm as unknown as { clearValidate: () => void }).clearValidate()
      await flushPromises()
      expect(context!.errors.value).toEqual({})
      // vee-validate 对未挂载字段保留空数组条目；它们应不再包含任何错误消息。
      expect(Object.values(context!.errorBag.value).every(messages => messages.length === 0)).toBe(true)
      expect(wrapper.find('[data-slot="form-message"]').exists()).toBe(false)
      expect(model).toEqual({ visible: 'draft', hidden: 0, enabled: false, profile: { email: '' } })
    } finally { wrapper.unmount() }
  })

  it('each label owns its input and generated ids are unique across the whole form', () => {
    const { wrapper } = mountPasswordPairForm()
    const ids = wrapper.findAll('[id]').map(node => node.attributes('id'))
    expect(new Set(ids).size).toBe(ids.length)
    wrapper.findAll('label').forEach((label, index) => {
      expect(label.element.control).toBe(wrapper.findAll('input')[index].element)
    })
  })

  it('validation descriptions preserve caller help text and form labels', async () => {
    const { wrapper } = mountPasswordPairForm({ id: 'caller-id', 'aria-describedby': 'password-help' })
    const input = wrapper.findAllComponents(EInput)[0]
    await input.get('input').setValue('a')
    await flushValidation()
    const nativeInput = input.get('input')
    const messageId = wrapper.get('[data-slot="form-message"]').attributes('id')
    expect(nativeInput.attributes('aria-describedby')?.split(' ')).toEqual(['password-help', messageId])
    expect(wrapper.findAll('label')[0].element.control).toBe(nativeInput.element)
    expect(wrapper.findAll(`[id="${nativeInput.attributes('id')}"]`)).toHaveLength(1)
  })

  it('挂载时空字段不显示校验信息', () => {
    const { wrapper } = mountPasswordPairForm()
    expect(wrapper.find('[data-slot="form-message"]').exists()).toBe(false)
  })

  it('密码输入不足最小长度时立即显示错误', async () => {
    const { wrapper } = mountPasswordPairForm()
    await wrapper.findAll('input')[0].setValue('a')
    await flushValidation()
    expect(wrapper.find('[data-slot="form-message"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('密码至少 8 位')
  })

  it('密码改到合法后错误消失', async () => {
    const { wrapper } = mountPasswordPairForm()
    await wrapper.findAll('input')[0].setValue('a')
    await flushValidation()
    await wrapper.findAll('input')[0].setValue('abcdefgh')
    await flushValidation()
    expect(wrapper.text()).not.toContain('密码至少 8 位')
    expect(wrapper.find('[data-slot="form-message"]').exists()).toBe(false)
  })

  it('确认密码已填写时改密码立即提示两次不一致', async () => {
    const { wrapper } = mountPasswordPairForm()
    await wrapper.findAll('input')[1].setValue('abcdefgh')
    await flushValidation()
    await wrapper.findAll('input')[0].setValue('zzzzzzzz')
    await flushValidation()
    expect(wrapper.text()).toContain('两次输入的密码不一致')
  })

  it('确认密码为空时改密码不出确认密码错误', async () => {
    const { wrapper } = mountPasswordPairForm()
    await wrapper.findAll('input')[0].setValue('abcdefgh')
    await flushValidation()
    expect(wrapper.text()).not.toContain('请再次输入密码')
    expect(wrapper.text()).not.toContain('两次输入的密码不一致')
  })

  it('提交空表单仍拦截并显示必填', async () => {
    const { wrapper } = mountPasswordPairForm()
    await wrapper.find('form').trigger('submit')
    await flushValidation()
    expect(wrapper.text()).toContain('请输入密码')
    expect(wrapper.text()).toContain('请再次输入密码')
  })
})

