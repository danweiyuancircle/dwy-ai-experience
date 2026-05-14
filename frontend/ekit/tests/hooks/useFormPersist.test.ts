/**
 * useFormPersist 单元测试
 * 覆盖：基础回填、敏感字段排除、reset、clear、storage 模式切换、自定义 exclude
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { useFormPersist, DEFAULT_SENSITIVE_FIELDS } from '@/hooks/useFormPersist'

describe('useFormPersist', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
  })

  describe('基础持久化', () => {
    it('刷新前后从 sessionStorage 恢复非敏感字段', async () => {
      const first = useFormPersist('form-1', { email: '', remark: '' })
      first.form.value.email = 'a@b.com'
      first.form.value.remark = '备注'
      await nextTick()

      // 模拟刷新：构造新的 composable 实例，应当从 storage 读回上次值
      const second = useFormPersist('form-1', { email: '', remark: '' })
      expect(second.form.value.email).toBe('a@b.com')
      expect(second.form.value.remark).toBe('备注')
    })

    it('未提供 key 对应的存储时使用 initialValue', () => {
      const { form } = useFormPersist('form-empty', { foo: 'default' })
      expect(form.value.foo).toBe('default')
    })
  })

  describe('敏感字段默认排除', () => {
    it('password 字段不会被写入 sessionStorage', async () => {
      const { form } = useFormPersist('form-pwd', { email: '', password: '' })
      form.value.email = 'a@b.com'
      form.value.password = 'secret123'
      await nextTick()

      const raw = sessionStorage.getItem('form-pwd')
      expect(raw).toBeTruthy()
      const parsed = JSON.parse(raw!)
      expect(parsed.email).toBe('a@b.com')
      expect(parsed).not.toHaveProperty('password')
    })

    it('刷新后 password 字段恢复为 initialValue 而非上次输入', async () => {
      const first = useFormPersist('form-pwd2', { email: '', password: '' })
      first.form.value.email = 'a@b.com'
      first.form.value.password = 'leaked'
      await nextTick()

      const second = useFormPersist('form-pwd2', { email: '', password: '' })
      expect(second.form.value.email).toBe('a@b.com')
      expect(second.form.value.password).toBe('')
    })

    it('内置敏感字段名清单符合预期', () => {
      expect(DEFAULT_SENSITIVE_FIELDS).toContain('password')
      expect(DEFAULT_SENSITIVE_FIELDS).toContain('code')
      expect(DEFAULT_SENSITIVE_FIELDS).toContain('token')
    })

    it('敏感字段名匹配不区分大小写', async () => {
      // 用户可能写 confirmPassword / ConfirmPassword 等驼峰
      const { form } = useFormPersist('form-pwd3', {
        email: '',
        ConfirmPassword: '',
      })
      form.value.email = 'a@b.com'
      form.value.ConfirmPassword = 'x'
      await nextTick()

      const parsed = JSON.parse(sessionStorage.getItem('form-pwd3')!)
      expect(parsed).not.toHaveProperty('ConfirmPassword')
    })
  })

  describe('自定义 exclude 追加', () => {
    it('调用方追加的字段也被排除', async () => {
      const { form } = useFormPersist(
        'form-custom',
        { email: '', nickname: '', internalId: '' },
        { exclude: ['internalId'] },
      )
      form.value.email = 'a@b.com'
      form.value.nickname = 'alice'
      form.value.internalId = 'should-not-persist'
      await nextTick()

      const parsed = JSON.parse(sessionStorage.getItem('form-custom')!)
      expect(parsed.email).toBe('a@b.com')
      expect(parsed.nickname).toBe('alice')
      expect(parsed).not.toHaveProperty('internalId')
    })
  })

  describe('reset / clear', () => {
    it('reset 把 form 还原到 initialValue 并清空 storage', async () => {
      const { form, reset } = useFormPersist('form-reset', { email: '', remark: '' })
      form.value.email = 'a@b.com'
      form.value.remark = 'hello'
      await nextTick()

      reset()
      await nextTick()
      expect(form.value.email).toBe('')
      expect(form.value.remark).toBe('')

      // 下一次 mount 不应该再恢复出旧值
      const next = useFormPersist('form-reset', { email: '', remark: '' })
      expect(next.form.value.email).toBe('')
      expect(next.form.value.remark).toBe('')
    })

    it('clear 只清存储不动当前 form', async () => {
      const { form, clear } = useFormPersist('form-clear', { email: '', remark: '' })
      form.value.email = 'a@b.com'
      await nextTick()

      clear()
      await nextTick()
      // 当前 form 保留输入
      expect(form.value.email).toBe('a@b.com')

      // 但下一次 mount 不会恢复
      const next = useFormPersist('form-clear', { email: '', remark: '' })
      expect(next.form.value.email).toBe('')
    })
  })

  describe('storage 介质切换', () => {
    it("storage='local' 时写入 localStorage，sessionStorage 干净", async () => {
      const { form } = useFormPersist(
        'form-local',
        { remark: '' },
        { storage: 'local' },
      )
      form.value.remark = 'persist across sessions'
      await nextTick()

      expect(localStorage.getItem('form-local')).toBeTruthy()
      expect(sessionStorage.getItem('form-local')).toBeNull()
    })
  })

  describe('disableDefaultExclude', () => {
    it('设为 true 时即使 password 字段也会落盘（仅用于完全无敏感字段的表单）', async () => {
      const { form } = useFormPersist(
        'form-no-default',
        { password: '' },
        { disableDefaultExclude: true },
      )
      form.value.password = 'whatever'
      await nextTick()

      const parsed = JSON.parse(sessionStorage.getItem('form-no-default')!)
      expect(parsed.password).toBe('whatever')
    })
  })
})
