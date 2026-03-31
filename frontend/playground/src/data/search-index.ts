import Fuse from 'fuse.js'

export interface SearchItem {
  title: string
  module: string
  path: string
  content: string
}

const searchItems: SearchItem[] = [
  // EUI components
  { title: 'Button 按钮', module: 'EUI 组件', path: '/eui/button', content: 'variant size loading disabled 按钮组件' },
  { title: 'Input 输入框', module: 'EUI 组件', path: '/eui/input', content: 'clearable password placeholder 输入框' },
  { title: 'Select 选择器', module: 'EUI 组件', path: '/eui/select', content: '下拉选择 options placeholder' },
  { title: 'Checkbox & Radio', module: 'EUI 组件', path: '/eui/checkbox-radio', content: '复选框 单选框' },
  { title: 'Switch 开关', module: 'EUI 组件', path: '/eui/switch', content: '切换开关' },
  { title: 'Form 表单', module: 'EUI 组件', path: '/eui/form', content: '表单验证 rules model' },
  { title: 'Table 表格', module: 'EUI 组件', path: '/eui/table', content: '数据表格 columns sortable selectable' },
  { title: 'Dialog 对话框', module: 'EUI 组件', path: '/eui/dialog-drawer', content: '对话框 抽屉 modal drawer' },
  { title: 'Toast 轻提示', module: 'EUI 组件', path: '/eui/toast', content: '消息提示 toast success error' },
  { title: 'Tabs 标签页', module: 'EUI 组件', path: '/eui/tabs', content: '标签页 tab' },
  { title: 'Menu 菜单', module: 'EUI 组件', path: '/eui/menu', content: '导航菜单 sidebar' },
  { title: 'Card 卡片', module: 'EUI 组件', path: '/eui/card', content: '卡片容器' },
  { title: 'Badge 徽标', module: 'EUI 组件', path: '/eui/alert-badge', content: '徽标 标签 badge' },
  { title: 'Alert 提示', module: 'EUI 组件', path: '/eui/alert-badge', content: '警告提示 alert' },
  { title: 'Tooltip 文字提示', module: 'EUI 组件', path: '/eui/tooltip-popover', content: '提示气泡 tooltip popover' },
  { title: 'Dropdown 下拉菜单', module: 'EUI 组件', path: '/eui/dropdown', content: '下拉菜单' },
  { title: 'Pagination 分页', module: 'EUI 组件', path: '/eui/pagination', content: '分页器' },
  { title: 'Breadcrumb 面包屑', module: 'EUI 组件', path: '/eui/breadcrumb', content: '面包屑导航' },
  { title: 'TagsInput 标签', module: 'EUI 组件', path: '/eui/tags-input', content: '标签输入' },
  { title: 'DatePicker 日期', module: 'EUI 组件', path: '/eui/date-time', content: '日期选择 时间选择 date time picker' },
  { title: 'Tree 树形控件', module: 'EUI 组件', path: '/eui/tree', content: '树形 tree node' },
  { title: 'Upload 上传', module: 'EUI 组件', path: '/eui/upload', content: '文件上传 drag' },
  { title: 'Progress 进度条', module: 'EUI 组件', path: '/eui/progress', content: '进度条' },
  { title: 'Accordion 手风琴', module: 'EUI 组件', path: '/eui/accordion', content: '手风琴 折叠面板' },
  { title: 'Stepper 步骤条', module: 'EUI 组件', path: '/eui/stepper', content: '步骤条 stepper' },
  { title: 'Carousel 走马灯', module: 'EUI 组件', path: '/eui/carousel', content: '轮播 carousel' },
  { title: 'Avatar 头像', module: 'EUI 组件', path: '/eui/avatar', content: '头像' },
  { title: 'Skeleton 骨架', module: 'EUI 组件', path: '/eui/skeleton', content: '骨架屏 loading' },
  { title: 'Slider 滑块', module: 'EUI 组件', path: '/eui/slider', content: '滑块 range' },
  { title: 'Rate 评分', module: 'EUI 组件', path: '/eui/rate', content: '评分 star' },
  { title: 'Transfer 穿梭框', module: 'EUI 组件', path: '/eui/transfer', content: '穿梭框' },
  { title: 'Descriptions 描述', module: 'EUI 组件', path: '/eui/descriptions', content: '描述列表' },
  { title: 'Timeline 时间线', module: 'EUI 组件', path: '/eui/timeline', content: '时间线' },
  { title: 'Statistic 统计', module: 'EUI 组件', path: '/eui/statistic', content: '统计数值' },
  { title: '业务组件', module: 'EUI 组件', path: '/eui/business', content: 'DataPage FormDialog ConfirmDialog 业务组件' },
  // Core modules
  { title: 'request 请求', module: 'Core 工具', path: '/core/request', content: 'createRequest axios plugin tokenPlugin unwrapPlugin refreshTokenPlugin 请求封装' },
  { title: 'storage 存储', module: 'Core 工具', path: '/core/storage', content: 'useStorage localStorage 响应式存储' },
  { title: 'validators 校验', module: 'Core 工具', path: '/core/validators', content: 'isPhone isEmail isIdCard isUrl isRequired 表单校验' },
  { title: 'date 日期', module: 'Core 工具', path: '/core/date', content: 'formatDate formatDateTime formatRelativeTime 日期格式化' },
  { title: 'hooks 组合式', module: 'Core 工具', path: '/core/hooks', content: 'useDebounce useClickOutside useEventListener composable' },
  // Backend modules
  { title: 'config 配置', module: 'Backend', path: '/backend/config', content: 'BaseSettings Pydantic Settings database_url secret_key 配置管理' },
  { title: 'database 数据库', module: 'Backend', path: '/backend/database', content: 'SQLAlchemy AsyncEngine Base TimestampMixin 异步数据库' },
  { title: 'security 安全', module: 'Backend', path: '/backend/security', content: 'JWT bcrypt hash_password create_token decode_token 认证' },
  { title: 'exceptions 异常', module: 'Backend', path: '/backend/exceptions', content: 'AppError NotFoundError BusinessError 异常处理' },
  { title: 'response 响应', module: 'Backend', path: '/backend/response', content: 'success fail paginated 统一响应' },
  { title: 'pagination 分页', module: 'Backend', path: '/backend/pagination', content: 'PaginationParams paginate OffsetLimit 分页工具' },
  { title: 'cache 缓存', module: 'Backend', path: '/backend/cache', content: 'Redis configure get_redis close_redis 缓存' },
  { title: 'dependencies 依赖', module: 'Backend', path: '/backend/dependencies', content: 'create_get_db FastAPI Depends 依赖注入' },
  // CLI
  { title: 'create-dwy', module: 'CLI', path: '/cli/create-dwy', content: 'dwy create dwy sync 项目脚手架 配置同步' },
  // Claude Code
  { title: 'dwy-frontend-eui', module: 'Claude Code', path: '/claude/skills/dwy-frontend-eui', content: 'EUI 组件库 skill Vue 3' },
  { title: 'dwy-frontend-core', module: 'Claude Code', path: '/claude/skills/dwy-frontend-core', content: 'Core 工具库 skill request storage' },
  { title: 'dwy-backend-base', module: 'Claude Code', path: '/claude/skills/dwy-backend-base', content: 'Backend 基础设施 skill FastAPI' },
  { title: 'server-security', module: 'Claude Code', path: '/claude/rules/server-security', content: '服务器安全 端口 Nginx Docker rule' },
  { title: 'git-security', module: 'Claude Code', path: '/claude/rules/git-security', content: 'Git 提交安全 敏感数据 rule' },
  { title: 'python-code-style', module: 'Claude Code', path: '/claude/rules/python-code-style', content: 'Python FastAPI 代码规范 rule' },
  { title: 'vue-code-style', module: 'Claude Code', path: '/claude/rules/vue-code-style', content: 'Vue 前端代码规范 rule' },
  { title: 'backend-security', module: 'Claude Code', path: '/claude/rules/backend-security', content: '后端安全规范 rule' },
  { title: 'pre-git-commit', module: 'Claude Code', path: '/claude/hooks/pre-git-commit-sensitive-check', content: '提交前敏感信息检查 hook' },
  { title: 'settings.json', module: 'Claude Code', path: '/claude/settings', content: 'Claude Code 配置 settings' },
]

const fuse = new Fuse(searchItems, {
  keys: [
    { name: 'title', weight: 2 },
    { name: 'content', weight: 1 },
    { name: 'module', weight: 0.5 },
  ],
  threshold: 0.4,
  includeScore: true,
})

export function search(query: string): SearchItem[] {
  if (!query.trim()) return []
  return fuse.search(query).map((r) => r.item)
}
