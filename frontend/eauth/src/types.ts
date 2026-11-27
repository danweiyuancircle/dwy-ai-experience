/** 管理员的安全身份投影；不包含应用用户、令牌、密码或权限推断。 */
export interface AdminIdentity { username: string }

/** 仅管理员 Cookie 协议；实现必须在登录失败、退出失败时 reject。 */
export interface AdminAuthApi {
  login(username: string, password: string): Promise<AdminIdentity>
  me(): Promise<AdminIdentity>
  logout(): Promise<void>
}

/** 仅在浏览器同源部署；跨源后端必须由宿主反向代理到本站。 */
export interface AdminAuthOptions {
  /** 管理 API 根路径或与当前页面同源的绝对 URL，不含 query/hash。 */
  baseURL: string
  /** me/logout 返回 401 时通知宿主；登录 401 交给表单展示。 */
  onSessionExpired?: () => void
}

/** 登录组件不持有路由或全局会话；宿主传入会话的 login 方法并处理成功事件。 */
export interface AdminLoginProps {
  /** 宿主管理员会话的 login 方法；不得传入 Google 用户认证实现。 */
  auth: Pick<AdminAuthApi, 'login'>
  /** 宿主品牌纯文本，不接受 HTML。 */
  brand: string
  /** 宿主信任的站内首页路径，不能来自 URL 查询参数。 */
  homePath: string
  /** 宿主固定的登录路径，用于阻止回跳登录页。 */
  loginPath: string
  /** 不可信的回跳参数；组件只接受安全站内路径。 */
  redirect?: string
  /** 由宿主解释服务状态后传入的提示，不渲染 HTML。 */
  initialError?: string
}
