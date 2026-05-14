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
  { title: 'Checkbox 复选框', module: 'EUI 组件', path: '/eui/checkbox', content: '复选框 多选 checkbox indeterminate' },
  { title: 'Radio 单选框', module: 'EUI 组件', path: '/eui/radio', content: '单选框 radio button' },
  { title: 'Switch 开关', module: 'EUI 组件', path: '/eui/switch', content: '切换开关' },
  { title: 'Form 表单', module: 'EUI 组件', path: '/eui/form', content: '表单验证 rules model' },
  { title: 'Table 表格', module: 'EUI 组件', path: '/eui/table', content: '数据表格 columns sortable selectable' },
  { title: 'Dialog 对话框', module: 'EUI 组件', path: '/eui/dialog', content: '对话框 modal 弹窗 draggable fullscreen' },
  { title: 'Drawer 抽屉', module: 'EUI 组件', path: '/eui/drawer', content: '抽屉 侧边面板 drawer direction' },
  { title: 'Toast 轻提示', module: 'EUI 组件', path: '/eui/toast', content: '消息提示 toast success error' },
  { title: 'Tabs 标签页', module: 'EUI 组件', path: '/eui/tabs', content: '标签页 tab' },
  { title: 'Menu 菜单', module: 'EUI 组件', path: '/eui/menu', content: '导航菜单 sidebar' },
  { title: 'Card 卡片', module: 'EUI 组件', path: '/eui/card', content: '卡片容器' },
  { title: 'Badge 徽标', module: 'EUI 组件', path: '/eui/badge', content: '徽标 标签 badge variant' },
  { title: 'Alert 提示', module: 'EUI 组件', path: '/eui/alert', content: '警告提示 alert closable destructive' },
  { title: 'Tooltip 文字提示', module: 'EUI 组件', path: '/eui/tooltip', content: '提示气泡 tooltip 悬停' },
  { title: 'Popover 气泡卡片', module: 'EUI 组件', path: '/eui/popover', content: '气泡卡片 popover 点击 富内容' },
  { title: 'Dropdown 下拉菜单', module: 'EUI 组件', path: '/eui/dropdown', content: '下拉菜单' },
  { title: 'Pagination 分页', module: 'EUI 组件', path: '/eui/pagination', content: '分页器' },
  { title: 'Breadcrumb 面包屑', module: 'EUI 组件', path: '/eui/breadcrumb', content: '面包屑导航' },
  { title: 'TagsInput 标签', module: 'EUI 组件', path: '/eui/tags-input', content: '标签输入' },
  { title: 'DatePicker 日期', module: 'EUI 组件', path: '/eui/date-picker', content: '日期选择 date picker 范围 月份 年份' },
  { title: 'TimePicker 时间', module: 'EUI 组件', path: '/eui/time-picker', content: '时间选择 time picker 步长' },
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
  { title: 'Typography 排版', module: 'EUI 组件', path: '/eui/typography', content: '排版 h1 h2 h3 lead muted' },
  { title: 'Kbd 键盘', module: 'EUI 组件', path: '/eui/kbd', content: '键盘按键 快捷键 keyboard' },
  { title: 'Separator 分隔线', module: 'EUI 组件', path: '/eui/separator', content: '分隔线 水平 垂直' },
  { title: 'Spinner 加载', module: 'EUI 组件', path: '/eui/spinner', content: '加载动画 loading spinner' },
  { title: 'Empty 空状态', module: 'EUI 组件', path: '/eui/empty', content: '空状态 暂无数据' },
  { title: 'Label 标签', module: 'EUI 组件', path: '/eui/label', content: '表单标签 label for' },
  { title: 'AspectRatio 宽高比', module: 'EUI 组件', path: '/eui/aspect-ratio', content: '宽高比 16:9 4:3' },
  { title: 'FormDialog 表单弹窗', module: 'EUI 组件', path: '/eui/form-dialog', content: '表单对话框 FormDialog loading confirm' },
  { title: 'ConfirmDialog 确认弹窗', module: 'EUI 组件', path: '/eui/confirm-dialog', content: '确认对话框 warning error 删除' },
  { title: 'DataPage 数据页', module: 'EUI 组件', path: '/eui/data-page', content: '数据列表页 搜索 分页 fetchFn' },
  { title: 'AlertDialog 警告对话框', module: 'EUI 组件', path: '/eui/alert-dialog', content: '警告对话框 确认 删除 alert-dialog confirm cancel' },
  { title: 'Sheet 侧边面板', module: 'EUI 组件', path: '/eui/sheet', content: '侧边面板 抽屉 sheet side top right bottom left' },
  { title: 'HoverCard 悬浮卡片', module: 'EUI 组件', path: '/eui/hover-card', content: '悬浮卡片 hover 鼠标悬停 用户信息' },
  { title: 'ContextMenu 右键菜单', module: 'EUI 组件', path: '/eui/context-menu', content: '右键菜单 上下文菜单 context-menu 复制 剪切' },
  { title: 'Collapsible 折叠面板', module: 'EUI 组件', path: '/eui/collapsible', content: '折叠 展开 collapsible toggle' },
  { title: 'ScrollArea 滚动区域', module: 'EUI 组件', path: '/eui/scroll-area', content: '滚动区域 自定义滚动条 scroll-area' },
  { title: 'Image 图片', module: 'EUI 组件', path: '/eui/image', content: '图片 懒加载 预览 fallback lazy preview' },
  { title: 'Calendar 日历', module: 'EUI 组件', path: '/eui/calendar', content: '日历 日期选择 多选 calendar' },
  { title: 'RangeCalendar 范围日历', module: 'EUI 组件', path: '/eui/range-calendar', content: '范围日历 日期区间 range-calendar' },
  { title: 'Toggle 切换按钮', module: 'EUI 组件', path: '/eui/toggle', content: '切换按钮 toggle on off 工具栏' },
  { title: 'ToggleGroup 切换按钮组', module: 'EUI 组件', path: '/eui/toggle-group', content: '切换按钮组 单选 多选 toggle group' },
  { title: 'ButtonGroup 按钮组', module: 'EUI 组件', path: '/eui/button-group', content: '按钮组 水平 垂直 button group' },
  { title: 'InputGroup 输入框组', module: 'EUI 组件', path: '/eui/input-group', content: '输入框组 前缀 后缀 addon input group' },
  { title: 'Resizable 可调整面板', module: 'EUI 组件', path: '/eui/resizable', content: '可调整面板 拖拽 分割 resizable panel splitter' },
  { title: 'InfiniteScroll 无限滚动', module: 'EUI 组件', path: '/eui/infinite-scroll', content: '无限滚动 加载更多 infinite scroll load' },
  { title: 'Affix 固钉', module: 'EUI 组件', path: '/eui/affix', content: '固钉 固定定位 sticky affix top bottom' },
  { title: 'Watermark 水印', module: 'EUI 组件', path: '/eui/watermark', content: '水印 版权 防截图 watermark opacity' },
  { title: 'Mention 提及', module: 'EUI 组件', path: '/eui/mention', content: '提及 @ 用户 mention at 选择' },
  // EKit modules
  { title: 'request 请求', module: 'EKit 工具', path: '/ekit/request', content: 'createRequest axios plugin tokenPlugin unwrapPlugin refreshTokenPlugin 请求封装' },
  { title: 'storage 存储', module: 'EKit 工具', path: '/ekit/storage', content: 'useStorage localStorage 响应式存储' },
  { title: 'validators 校验', module: 'EKit 工具', path: '/ekit/validators', content: 'isPhone isEmail isIdCard isUrl isRequired 表单校验' },
  { title: 'date 日期', module: 'EKit 工具', path: '/ekit/date', content: 'formatDate formatDateTime formatRelativeTime 日期格式化' },
  { title: 'hooks 组合式', module: 'EKit 工具', path: '/ekit/hooks', content: 'useDebounce useClickOutside useEventListener composable' },
  // EApi modules
  { title: 'config 配置', module: 'EApi', path: '/eapi/config', content: 'BaseSettings Pydantic Settings database_url secret_key 配置管理' },
  { title: 'database 数据库', module: 'EApi', path: '/eapi/database', content: 'SQLAlchemy AsyncEngine Base TimestampMixin 异步数据库' },
  { title: 'security 安全', module: 'EApi', path: '/eapi/security', content: 'JWT bcrypt hash_password create_token decode_token 认证' },
  { title: 'exceptions 异常', module: 'EApi', path: '/eapi/exceptions', content: 'AppError NotFoundError BusinessError 异常处理' },
  { title: 'response 响应', module: 'EApi', path: '/eapi/response', content: 'success fail paginated 统一响应' },
  { title: 'pagination 分页', module: 'EApi', path: '/eapi/pagination', content: 'PaginationParams paginate OffsetLimit 分页工具' },
  { title: 'cache 缓存', module: 'EApi', path: '/eapi/cache', content: 'Redis configure get_redis close_redis 缓存' },
  { title: 'dependencies 依赖', module: 'EApi', path: '/eapi/dependencies', content: 'create_get_db FastAPI Depends 依赖注入' },
  // CLI
  { title: 'create-dwy', module: 'CLI', path: '/cli/create-dwy', content: 'dwy create dwy sync 项目脚手架 配置同步' },
  // Claude Code · Skills
  { title: 'dwy-eui', module: 'Claude Code', path: '/claude/skills/dwy-eui', content: 'EUI 组件库 skill Vue 3 reka-ui shadcn' },
  { title: 'dwy-ekit', module: 'Claude Code', path: '/claude/skills/dwy-ekit', content: 'EKit 工具库 skill request storage validators date hooks' },
  { title: 'dwy-eapi', module: 'Claude Code', path: '/claude/skills/dwy-eapi', content: 'EApi 基础设施 skill FastAPI SQLAlchemy Redis' },
  { title: 'dwy-cli-sync-local', module: 'Claude Code', path: '/claude/skills/dwy-cli-sync-local', content: 'CLI 发版后同步本地全局 dwy 命令 skill npm publish' },
  { title: 'dwy-dev-qa', module: 'Claude Code', path: '/claude/skills/dwy-dev-qa', content: '开发质量保障流程 code review 测试 skill' },
  { title: 'dwy-pentest', module: 'Claude Code', path: '/claude/skills/dwy-pentest', content: '白帽渗透测试 安全评估 漏洞扫描 skill' },
  { title: 'dwy-publish', module: 'Claude Code', path: '/claude/skills/dwy-publish', content: '发版流程 测试 bump changelog publish tag skill' },
  // Claude Code · Rules · 技术选型与项目结构
  { title: 'dwy-tech-stack', module: 'Claude Code', path: '/claude/rules/dwy-tech-stack', content: '跨栈技术选型强制约束 FastAPI Vue Flutter rule' },
  { title: 'dwy-project-structure', module: 'Claude Code', path: '/claude/rules/dwy-project-structure', content: '项目结构 monorepo 目录约定 rule' },
  { title: 'dwy-prefer-open-source', module: 'Claude Code', path: '/claude/rules/dwy-prefer-open-source', content: '优先成熟开源方案 不重复造轮子 rule' },
  // Claude Code · Rules · 开发流程与提交
  { title: 'dwy-tdd-development', module: 'Claude Code', path: '/claude/rules/dwy-tdd-development', content: 'TDD 测试驱动开发 先测试后代码 rule' },
  { title: 'dwy-git-commit-convention', module: 'Claude Code', path: '/claude/rules/dwy-git-commit-convention', content: 'Git commit 规范 type scope subject rule' },
  { title: 'dwy-git-security', module: 'Claude Code', path: '/claude/rules/dwy-git-security', content: 'Git 提交安全 敏感数据 .env 密钥 rule' },
  // Claude Code · Rules · 安全
  { title: 'dwy-server-security', module: 'Claude Code', path: '/claude/rules/dwy-server-security', content: '服务器安全 端口 Nginx Docker rule' },
  { title: 'dwy-payload-limits', module: 'Claude Code', path: '/claude/rules/dwy-payload-limits', content: '数据载荷三层长度限制 前端 网关 后端 rule' },
  // Claude Code · Rules · API 与数据库
  { title: 'dwy-api-design', module: 'Claude Code', path: '/claude/rules/dwy-api-design', content: 'API 设计 RESTful 路径 命名 rule' },
  { title: 'dwy-db-migration', module: 'Claude Code', path: '/claude/rules/dwy-db-migration', content: '数据库迁移 Alembic schema rule' },
  // Claude Code · Rules · Python 后端
  { title: 'dwy-python-core', module: 'Claude Code', path: '/claude/rules/dwy-python-core', content: 'Python 基础风格 类型标注 注释 rule' },
  { title: 'dwy-python-fastapi', module: 'Claude Code', path: '/claude/rules/dwy-python-fastapi', content: 'FastAPI 路由 依赖注入 中间件 rule' },
  { title: 'dwy-python-orm', module: 'Claude Code', path: '/claude/rules/dwy-python-orm', content: 'SQLAlchemy 异步 ORM 模型 关联 rule' },
  { title: 'dwy-python-security', module: 'Claude Code', path: '/claude/rules/dwy-python-security', content: 'Python 后端安全 输入校验 注入 rule' },
  { title: 'dwy-python-testing', module: 'Claude Code', path: '/claude/rules/dwy-python-testing', content: 'Python 测试 pytest fixture rule' },
  // Claude Code · Rules · Vue 前端
  { title: 'dwy-vue-core', module: 'Claude Code', path: '/claude/rules/dwy-vue-core', content: 'Vue 3 基础风格 Composition API setup rule' },
  { title: 'dwy-vue-api', module: 'Claude Code', path: '/claude/rules/dwy-vue-api', content: 'Vue API 调用 axios 请求 rule' },
  { title: 'dwy-vue-pinia', module: 'Claude Code', path: '/claude/rules/dwy-vue-pinia', content: 'Pinia Setup Store 状态管理 rule' },
  { title: 'dwy-vue-testing', module: 'Claude Code', path: '/claude/rules/dwy-vue-testing', content: 'Vue 测试 Vitest jsdom rule' },
  // Claude Code · Rules · Flutter 移动端
  { title: 'dwy-flutter-core', module: 'Claude Code', path: '/claude/rules/dwy-flutter-core', content: 'Flutter Riverpod 基础风格 rule' },
  { title: 'dwy-flutter-network', module: 'Claude Code', path: '/claude/rules/dwy-flutter-network', content: 'Flutter Dio 网络请求 rule' },
  { title: 'dwy-flutter-router', module: 'Claude Code', path: '/claude/rules/dwy-flutter-router', content: 'Flutter GoRouter 路由 rule' },
  { title: 'dwy-flutter-testing', module: 'Claude Code', path: '/claude/rules/dwy-flutter-testing', content: 'Flutter 测试 widget integration rule' },
  // Claude Code · Rules · 基础设施
  { title: 'dwy-docker-spec', module: 'Claude Code', path: '/claude/rules/dwy-docker-spec', content: 'Docker Compose 容器化 rule' },
  // Claude Code · Hooks
  { title: 'pre-git-commit', module: 'Claude Code', path: '/claude/hooks/pre-git-commit-sensitive-check', content: '提交前敏感信息检查 hook' },
  // Blocks
  { title: 'Login 居中卡片', module: 'EUI 组件', path: '/eui/blocks/login-01', content: 'login 登录 卡片 block' },
  { title: 'Login 双栏图片', module: 'EUI 组件', path: '/eui/blocks/login-02', content: 'login 登录 双栏 图片 block' },
  { title: 'Login 卡片图片', module: 'EUI 组件', path: '/eui/blocks/login-04', content: 'login 登录 卡片 图片 block' },
  { title: 'OTP 验证码', module: 'EUI 组件', path: '/eui/blocks/otp-01', content: 'otp 验证码 block' },
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
