/** 管理员 Cookie 登录表单；需宿主 EConfigProvider、EUI/Tailwind 样式和成功后的导航处理。 */
export { default as AdminLogin } from './AdminLogin.vue'
export { createAdminAuthApi, AdminAuthError } from './api'
export { createAdminSession } from './session'
export type { AdminAuthApi, AdminAuthOptions, AdminIdentity, AdminLoginProps } from './types'
