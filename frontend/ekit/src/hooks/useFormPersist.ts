/**
 * useFormPersist：让表单字段在页面刷新后自动回填，提升填写中途意外刷新的体验
 *
 * 安全策略：
 * - 默认排除一组常见敏感字段（密码 / 验证码 / token 等），即使调用方忘记声明也不会落盘
 * - 默认走 sessionStorage（关闭标签页即清，避免敏感残留），可改 localStorage
 * - 调用方可通过 exclude 追加项目自定义敏感字段名
 *
 * 典型用法：
 * ```ts
 * const { form, reset } = useFormPersist('register-form', {
 *   email: '',
 *   code: '',
 *   password: '',
 * })
 * // 提交成功后清空
 * await api.register(form.value)
 * reset()
 * ```
 */
import { ref, watch, type Ref } from 'vue'
import { useStorage } from '@vueuse/core'

/**
 * 默认排除的敏感字段名（不区分大小写）
 * 这些字段名在表单中通常承载明文凭证或一次性令牌，落到 storage 是 OWASP 反模式
 */
export const DEFAULT_SENSITIVE_FIELDS: readonly string[] = [
  'password',
  'confirmPassword',
  'oldPassword',
  'newPassword',
  'pwd',
  'code',
  'captcha',
  'verifyCode',
  'verificationCode',
  'smsCode',
  'emailCode',
  'phoneCode',
  'otp',
  'token',
  'accessToken',
  'refreshToken',
  'signSecret',
  'secret',
  'apiKey',
]

/**
 * useFormPersist 配置项
 */
export interface UseFormPersistOptions<T> {
  /** 追加排除的字段名（与默认敏感字段名合并），这些字段不会写入 storage */
  exclude?: (keyof T)[]
  /** 存储介质，默认 'session'（关闭标签页清除），'local' 跨会话保留 */
  storage?: 'session' | 'local'
  /**
   * 是否禁用内置敏感字段排除清单。默认 false（开启内置排除）。
   * 仅在你确认整个表单都不含敏感凭证时才设 true，否则会有泄露风险
   */
  disableDefaultExclude?: boolean
}

/**
 * useFormPersist 返回值
 */
export interface UseFormPersistReturn<T> {
  /** 响应式表单数据，可直接 v-model 绑定到表单字段 */
  form: Ref<T>
  /** 重置 form 到 initialValue，并清空持久化存储 */
  reset: () => void
  /** 仅清空持久化存储，不修改当前 form 值 */
  clear: () => void
}

/**
 * 让表单字段在浏览器刷新后自动回填，敏感字段（密码 / 验证码 / token 等）被默认排除
 * @param key 持久化键名，跨页面唯一
 * @param initialValue 表单初始值，类型推导从此处取
 * @param options 配置项：exclude 追加敏感字段、storage 选择介质、disableDefaultExclude 关闭内置排除
 * @returns form / reset / clear
 */
export function useFormPersist<T extends Record<string, unknown>>(
  key: string,
  initialValue: T,
  options: UseFormPersistOptions<T> = {},
): UseFormPersistReturn<T> {
  const { exclude = [], storage = 'session', disableDefaultExclude = false } = options

  const sensitiveSet = new Set<string>([
    ...exclude.map((k) => String(k).toLowerCase()),
    ...(disableDefaultExclude ? [] : DEFAULT_SENSITIVE_FIELDS.map((k) => k.toLowerCase())),
  ])

  /**
   * 从对象中挑出可持久化的字段（剔除敏感字段）
   * @param obj 源对象
   */
  function pickPersistable(obj: T): Partial<T> {
    const next: Partial<T> = {}
    for (const k of Object.keys(obj) as (keyof T)[]) {
      if (!sensitiveSet.has(String(k).toLowerCase())) {
        next[k] = obj[k]
      }
    }
    return next
  }

  // 走 sessionStorage 还是 localStorage —— vueuse useStorage 第三参数支持自定义 Storage 实例
  const storageArea = storage === 'local' ? window.localStorage : window.sessionStorage
  const persistedInitial = pickPersistable(initialValue)
  const storageRef = useStorage<Partial<T>>(key, persistedInitial, storageArea, {
    mergeDefaults: true,
  })

  // 把存储里读回来的非敏感字段合到 initialValue 上作为 form 起始值；敏感字段始终为 initialValue 中的值
  const form = ref<T>({ ...initialValue, ...storageRef.value }) as Ref<T>

  watch(
    form,
    (val) => {
      storageRef.value = pickPersistable(val)
    },
    { deep: true },
  )

  /**
   * 重置 form 到 initialValue，并清空持久化存储
   */
  function reset() {
    form.value = { ...initialValue }
    storageRef.value = persistedInitial
  }

  /**
   * 仅清空持久化存储，不动当前 form
   */
  function clear() {
    storageRef.value = persistedInitial
  }

  return { form, reset, clear }
}
