import { computed, shallowRef } from 'vue'
import type { AdminAuthApi, AdminIdentity } from './types'

/** 每个宿主实例独立创建；身份只存内存，刷新必须向服务器校验 Cookie。 */
export function createAdminSession(api: AdminAuthApi) {
  const identity = shallowRef<AdminIdentity | null>(null)
  let generation = 0

  async function authenticate(action: () => Promise<AdminIdentity>): Promise<AdminIdentity> {
    const current = ++generation
    try {
      const result = await action()
      if (current === generation) identity.value = { username: result.username }
      return result
    } catch (cause) {
      if (current === generation) identity.value = null
      throw cause
    }
  }
  return {
    /** 只读管理身份，不作为后端授权依据。 */
    administrator: computed(() => identity.value),
    /** 登录后保存服务端身份；密码不持久化。 */
    login: (username: string, password: string) => authenticate(() => api.login(username, password)),
    /** 每次新页面会话先向服务端校验 HttpOnly Cookie。 */
    restore: () => authenticate(() => api.me()),
    /** 只有服务端撤销成功才清空身份；失败保留重试入口。 */
    async logout() { await api.logout(); generation++; identity.value = null },
    /** 收到宿主业务 API 的 401 时调用，阻止旧响应恢复过期身份。 */
    invalidate() { generation++; identity.value = null },
  }
}
