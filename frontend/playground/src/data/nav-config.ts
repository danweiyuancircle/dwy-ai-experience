export interface NavItem {
  name: string
  path: string
}

export interface NavCategory {
  title: string
  items: NavItem[]
}

export interface ModuleConfig {
  key: string
  label: string
  prefix: string
  categories: NavCategory[]
}

export const modules: ModuleConfig[] = [
  {
    key: 'eui',
    label: 'EUI 组件',
    prefix: '/eui',
    categories: [
      {
        title: '基础 Basic',
        items: [
          { name: 'Button 按钮', path: '/eui/button' },
          { name: 'Badge 徽标', path: '/eui/alert-badge' },
          { name: 'Alert 提示', path: '/eui/alert-badge' },
          { name: 'Card 卡片', path: '/eui/card' },
          { name: 'Avatar 头像', path: '/eui/avatar' },
          { name: 'Typography 排版', path: '/eui/misc' },
        ],
      },
      {
        title: '表单 Form',
        items: [
          { name: 'Input 输入框', path: '/eui/input' },
          { name: 'Select 选择器', path: '/eui/select' },
          { name: 'Checkbox & Radio', path: '/eui/checkbox-radio' },
          { name: 'Switch 开关', path: '/eui/switch' },
          { name: 'Slider 滑块', path: '/eui/slider' },
          { name: 'Rate 评分', path: '/eui/rate' },
          { name: 'DatePicker 日期', path: '/eui/date-time' },
          { name: 'TagsInput 标签', path: '/eui/tags-input' },
          { name: 'Upload 上传', path: '/eui/upload' },
          { name: 'Form 表单', path: '/eui/form' },
        ],
      },
      {
        title: '数据展示 Data',
        items: [
          { name: 'Table 表格', path: '/eui/table' },
          { name: 'Descriptions 描述', path: '/eui/descriptions' },
          { name: 'Statistic 统计', path: '/eui/statistic' },
          { name: 'Timeline 时间线', path: '/eui/timeline' },
          { name: 'Tree 树形控件', path: '/eui/tree' },
          { name: 'Progress 进度条', path: '/eui/progress' },
          { name: 'Skeleton 骨架', path: '/eui/skeleton' },
          { name: 'Carousel 走马灯', path: '/eui/carousel' },
        ],
      },
      {
        title: '导航 Navigation',
        items: [
          { name: 'Tabs 标签页', path: '/eui/tabs' },
          { name: 'Menu 菜单', path: '/eui/menu' },
          { name: 'Breadcrumb 面包屑', path: '/eui/breadcrumb' },
          { name: 'Pagination 分页', path: '/eui/pagination' },
          { name: 'Dropdown 下拉菜单', path: '/eui/dropdown' },
          { name: 'Stepper 步骤条', path: '/eui/stepper' },
        ],
      },
      {
        title: '反馈 Feedback',
        items: [
          { name: 'Dialog 对话框', path: '/eui/dialog-drawer' },
          { name: 'Drawer 抽屉', path: '/eui/dialog-drawer' },
          { name: 'Toast 轻提示', path: '/eui/toast' },
          { name: 'Tooltip 提示', path: '/eui/tooltip-popover' },
          { name: 'Popover 气泡', path: '/eui/tooltip-popover' },
        ],
      },
      {
        title: '其他 Other',
        items: [
          { name: 'Accordion 手风琴', path: '/eui/accordion' },
          { name: 'Transfer 穿梭框', path: '/eui/transfer' },
          { name: 'Misc 杂项', path: '/eui/misc' },
          { name: '业务组件', path: '/eui/business' },
        ],
      },
    ],
  },
  {
    key: 'core',
    label: 'Core 工具',
    prefix: '/core',
    categories: [
      {
        title: '模块',
        items: [
          { name: '概览', path: '/core' },
          { name: 'request 请求', path: '/core/request' },
          { name: 'storage 存储', path: '/core/storage' },
          { name: 'validators 校验', path: '/core/validators' },
          { name: 'date 日期', path: '/core/date' },
          { name: 'hooks 组合式', path: '/core/hooks' },
        ],
      },
    ],
  },
  {
    key: 'backend',
    label: 'Backend',
    prefix: '/backend',
    categories: [
      {
        title: '模块',
        items: [
          { name: '概览', path: '/backend' },
          { name: 'config 配置', path: '/backend/config' },
          { name: 'database 数据库', path: '/backend/database' },
          { name: 'security 安全', path: '/backend/security' },
          { name: 'exceptions 异常', path: '/backend/exceptions' },
          { name: 'response 响应', path: '/backend/response' },
          { name: 'pagination 分页', path: '/backend/pagination' },
          { name: 'cache 缓存', path: '/backend/cache' },
          { name: 'dependencies 依赖', path: '/backend/dependencies' },
        ],
      },
    ],
  },
  {
    key: 'cli',
    label: 'CLI',
    prefix: '/cli',
    categories: [
      {
        title: '命令',
        items: [
          { name: '概览', path: '/cli' },
          { name: 'create-dwy', path: '/cli/create-dwy' },
        ],
      },
    ],
  },
  {
    key: 'claude',
    label: 'Claude Code',
    prefix: '/claude',
    categories: [
      {
        title: '概览',
        items: [
          { name: '概览', path: '/claude' },
        ],
      },
      {
        title: 'Skills',
        items: [
          { name: 'dwy-frontend-eui', path: '/claude/skills/dwy-frontend-eui' },
          { name: 'dwy-frontend-core', path: '/claude/skills/dwy-frontend-core' },
          { name: 'dwy-backend-base', path: '/claude/skills/dwy-backend-base' },
        ],
      },
      {
        title: 'Rules',
        items: [
          { name: 'server-security', path: '/claude/rules/server-security' },
          { name: 'git-security', path: '/claude/rules/git-security' },
          { name: 'python-code-style', path: '/claude/rules/python-code-style' },
          { name: 'vue-code-style', path: '/claude/rules/vue-code-style' },
          { name: 'backend-security', path: '/claude/rules/backend-security' },
        ],
      },
      {
        title: 'Hooks',
        items: [
          { name: 'pre-git-commit', path: '/claude/hooks/pre-git-commit-sensitive-check' },
        ],
      },
      {
        title: 'Settings',
        items: [
          { name: 'settings.json', path: '/claude/settings' },
        ],
      },
    ],
  },
]

export function getModuleByPath(path: string): ModuleConfig | undefined {
  return modules.find((m) => path === m.prefix || path.startsWith(m.prefix + '/'))
}

export function getActiveModuleKey(path: string): string {
  if (path === '/') return 'eui'
  const mod = getModuleByPath(path)
  return mod?.key ?? 'eui'
}
