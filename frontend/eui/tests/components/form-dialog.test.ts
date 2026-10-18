import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { h } from 'vue'
import { describe, it, expect, afterEach } from 'vitest'
import EFormDialog from '@/components/form-dialog/EFormDialog.vue'
import EForm from '@/components/form/EForm.vue'

enableAutoUnmount(afterEach)

describe('EFormDialog', () => {
  it('renders without error when closed', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders without error when open', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: true, title: 'Edit User' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, title: 'Create Item' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts loading prop', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, loading: true },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom button text props', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, confirmText: 'Save', cancelText: 'Discard' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts slot content', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, title: 'Test' },
      slots: { default: '<p>Form fields</p>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it.each(['Escape', '遮罩'])('loading 期间阻止 %s 关闭，结束后恢复关闭', async (action) => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, loading: true, title: '编辑' },
    })
    await flushPromises()

    // 使用真实 reka 关闭交互，避免只断言透传 prop 而漏掉弹层内部状态变化。
    const dismiss = async () => {
      if (action === 'Escape') {
        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }))
      } else {
        const overlay = document.querySelector('[data-slot="dialog-overlay"]')!
        overlay.dispatchEvent(new MouseEvent('pointerdown', { bubbles: true, button: 0 }))
      }
      await flushPromises()
    }

    await dismiss()
    expect(wrapper.emitted('update:open')).toBeUndefined()
    expect(document.querySelector('[data-slot="dialog-content"]')).not.toBeNull()

    await wrapper.setProps({ loading: false })
    await dismiss()
    expect(wrapper.emitted('update:open')).toEqual([[false]])
    expect(document.querySelector('[data-slot="dialog-overlay"]')).toBeNull()
  })

  it('loading 期间隐藏关闭按钮，结束后恢复 X 关闭', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, loading: true, title: '编辑' },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-close"]')).toBeNull()

    await wrapper.setProps({ loading: false })
    const close = document.querySelector<HTMLButtonElement>('[data-slot="dialog-close"]')!
    close.click()
    await flushPromises()
    expect(wrapper.emitted('update:open')).toEqual([[false]])
  })

  it('loading 禁用取消与确认，结束后取消恢复事件与关闭', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, loading: true, title: '编辑' },
    })
    await flushPromises()
    const [cancel, confirm] = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')
    expect(cancel.disabled).toBe(true)
    expect(confirm.disabled).toBe(true)
    cancel.click()
    confirm.click()
    confirm.click()
    await flushPromises()
    expect(wrapper.emitted('cancel')).toBeUndefined()
    expect(wrapper.emitted('confirm')).toBeUndefined()
    expect(wrapper.emitted('update:open')).toBeUndefined()

    await wrapper.setProps({ loading: false })
    cancel.click()
    await flushPromises()
    expect(wrapper.emitted('cancel')).toEqual([[]])
    expect(wrapper.emitted('update:open')?.every(([open]) => open === false)).toBe(true)
  })

  it('确认开始 loading 后不重复提交，结束后可重试', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑' },
    })
    await flushPromises()
    const confirm = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')[1]
    confirm.click()
    await wrapper.setProps({ loading: true })
    confirm.click()
    confirm.click()
    await flushPromises()
    expect(wrapper.emitted('confirm')).toEqual([[]])

    await wrapper.setProps({ loading: false })
    confirm.click()
    await flushPromises()
    expect(wrapper.emitted('confirm')).toEqual([[], []])
  })

  it('loading 期间父组件仍能通过 open=false 收起', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, loading: true, title: '编辑' },
    })
    await flushPromises()
    await wrapper.setProps({ open: false })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-overlay"]')).toBeNull()
    expect(wrapper.emitted('cancel')).toBeUndefined()
  })

  it('confirmDisabled 禁止确认但保留取消，恢复后允许确认', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, confirmDisabled: true, title: '编辑' },
    })
    await flushPromises()
    const [cancel, confirm] = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')
    expect(cancel.disabled).toBe(false)
    expect(confirm.disabled).toBe(true)
    // 显式派发事件覆盖 handler 约束：调用方不能靠绕过原生 disabled 触发无效确认。
    confirm.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await flushPromises()
    expect(wrapper.emitted('confirm')).toBeUndefined()

    await wrapper.setProps({ confirmDisabled: false })
    confirm.click()
    await flushPromises()
    expect(wrapper.emitted('confirm')).toEqual([[]])
  })

  it('form 关联默认确认按钮，点击只触发一次真实 EForm 提交', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑', form: 'edit-user' },
      slots: {
        default: () => h(EForm, { id: 'edit-user', model: { first: 'one', second: 'two' } }, () => [
          h('input', { name: 'first', value: 'one' }),
          h('input', { name: 'second', value: 'two' }),
        ]),
      },
    })
    await flushPromises()
    const form = wrapper.findComponent(EForm)
    const formElement = document.querySelector<HTMLFormElement>('#edit-user')!
    const confirm = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')[1]
    expect(formElement.contains(confirm)).toBe(false)
    expect(confirm.form).toBe(formElement)
    expect(confirm.type).toBe('submit')

    // 使用真实按钮激活行为，经原生 submit 进入 EForm 校验与提交，不手工派发 submit。
    confirm.click()
    await flushPromises()
    expect(form.emitted('submit')).toEqual([[{ first: 'one', second: 'two' }]])
    expect(wrapper.emitted('confirm')).toBeUndefined()
  })

  it.each(['loading', 'confirmDisabled'] as const)('关联 form 时 %s 阻止提交，恢复后可提交', async (state) => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑', form: 'disabled-user', [state]: true },
      slots: {
        default: () => h(EForm, { id: 'disabled-user', model: { name: 'test' } }, () => h('input', { name: 'name' })),
      },
    })
    await flushPromises()
    const form = wrapper.findComponent(EForm)
    const confirm = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')[1]
    expect(confirm.disabled).toBe(true)
    confirm.click()
    await flushPromises()
    expect(form.emitted('submit')).toBeUndefined()
    expect(wrapper.emitted('confirm')).toBeUndefined()

    await wrapper.setProps({ [state]: false })
    confirm.click()
    await flushPromises()
    expect(form.emitted('submit')).toEqual([[{ name: 'test' }]])
    expect(wrapper.emitted('confirm')).toBeUndefined()
  })

  it('未关联 form 时默认确认为普通按钮，保留 confirm 事件', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑' },
    })
    await flushPromises()
    const confirm = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')[1]
    expect(confirm.type).toBe('button')
    expect(confirm.form).toBeNull()
    confirm.click()
    await flushPromises()
    expect(wrapper.emitted('confirm')).toEqual([[]])
  })

  it('description 作为可访问对话框说明显示', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑', description: '修改仅影响当前配置' },
    })
    await flushPromises()
    const description = document.querySelector('[data-slot="dialog-description"]')!
    const dialog = document.querySelector('[data-slot="dialog-content"]')!
    expect(description.textContent).toBe('修改仅影响当前配置')
    expect(dialog.getAttribute('aria-describedby')).toBe(description.id)
    wrapper.unmount()
  })

  it('footer-leading 位于默认按钮之前并保留默认确认行为', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑' },
      slots: { 'footer-leading': '<button type="button">恢复默认</button>' },
    })
    await flushPromises()
    const buttons = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')
    expect(Array.from(buttons, button => button.textContent?.trim())).toEqual(['恢复默认', '取消', '确认'])
    buttons[2].click()
    await flushPromises()
    expect(wrapper.emitted('confirm')).toEqual([[]])
  })

  it('footer 仍可整体覆盖默认按钮及 footer-leading', async () => {
    mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑' },
      slots: {
        'footer-leading': '<button type="button">恢复默认</button>',
        footer: '<button type="button">自定义操作</button>',
      },
    })
    await flushPromises()
    const buttons = document.querySelectorAll<HTMLButtonElement>('[data-slot="dialog-footer"] button')
    expect(Array.from(buttons, button => button.textContent)).toEqual(['自定义操作'])
  })

  it('打开时有 DialogDescription，避免 reka 缺 description 警告', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: 'Edit User' },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-description"]')).not.toBeNull()
    wrapper.unmount()
  })
})
