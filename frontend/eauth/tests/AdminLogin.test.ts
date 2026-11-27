import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import AdminLogin from '../src/AdminLogin.vue'

const wrappers: ReturnType<typeof mount>[] = []
afterEach(() => wrappers.splice(0).forEach(wrapper => wrapper.unmount()))
function render(login: ReturnType<typeof vi.fn>, redirect = '/') {
  const wrapper = mount(AdminLogin, { props: { auth: { login }, brand: 'Test Console', redirect, homePath: '/dashboard', loginPath: '/sign-in' } })
  wrappers.push(wrapper)
  return wrapper
}
it('品牌注入，真实表单的输入上界与错误反馈，失败不会导航', async () => {
  const login = vi.fn().mockRejectedValue(new Error('用户名或密码错误')), wrapper = render(login)
  expect(wrapper.text()).toContain('Test Console')
  expect(wrapper.text()).toContain('管理账户与应用用户账户独立')
  expect(wrapper.get('input[name="username"]').attributes('maxlength')).toBe('64')
  expect(wrapper.get('input[name="password"]').attributes('maxlength')).toBe('256')
  await wrapper.get('input[name="password"]').setValue('wrong')
  await wrapper.get('form').trigger('submit'); await flushPromises()
  expect(wrapper.text()).toContain('用户名或密码错误')
  expect(wrapper.emitted('authenticated')).toBeUndefined()
})
it.each(['https://foreign.invalid/', '//foreign.invalid/', '/\\foreign.invalid/', '/sign-in?redirect=/secret', '/%5cforeign.invalid/', '/a\n/b'])('拒绝危险回跳 %s，使用注入首页', async redirect => {
  const wrapper = render(vi.fn().mockResolvedValue({ username: 'admin' }), redirect)
  await wrapper.get('input[name="password"]').setValue('test-only-password')
  await wrapper.get('form').trigger('submit'); await flushPromises()
  expect(wrapper.emitted('authenticated')?.[0]).toEqual([{ username: 'admin' }, '/dashboard'])
  expect((wrapper.get('input[name="password"]').element as HTMLInputElement).value).toBe('')
})
it('允许站内回跳，等待中禁止重复提交', async () => {
  let finish!: (value: { username: string }) => void
  const login = vi.fn().mockReturnValue(new Promise(resolve => { finish = resolve })), wrapper = render(login, '/reports?period=week')
  await wrapper.get('input[name="password"]').setValue('test-only-password')
  await wrapper.get('form').trigger('submit'); await wrapper.get('form').trigger('submit')
  expect(login).toHaveBeenCalledOnce()
  finish({ username: 'admin' }); await flushPromises()
  expect(wrapper.emitted('authenticated')?.[0]?.[1]).toBe('/reports?period=week')
})
it('脚本提交超限密码时也不调用 API', async () => {
  const login = vi.fn(), wrapper = render(login)
  await wrapper.get('input[name="password"]').setValue('x'.repeat(257))
  await wrapper.get('form').trigger('submit'); await flushPromises()
  expect(login).not.toHaveBeenCalled()
  expect(wrapper.text()).toContain('256')
})
