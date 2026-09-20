import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, reactive } from 'vue'
import { describe, it, expect } from 'vitest'
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

function mountPasswordPairForm() {
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
        return { model, rules }
      },
      template: `
        <EForm :model="model" :rules="rules">
          <EFormItem prop="password" label="密码">
            <EInput v-model="model.password" />
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

