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
        title: '开始 Getting Started',
        items: [
          { name: '概览', path: '/eui' },
          { name: '集成指南', path: '/eui/integration' },
        ],
      },
      {
        title: '基础 Basic',
        items: [
          { name: 'Button 按钮', path: '/eui/button' },
          { name: 'ButtonGroup 按钮组', path: '/eui/button-group' },
          { name: 'Toggle 切换按钮', path: '/eui/toggle' },
          { name: 'ToggleGroup 切换按钮组', path: '/eui/toggle-group' },
          { name: 'Badge 徽标', path: '/eui/badge' },
          { name: 'Alert 提示', path: '/eui/alert' },
          { name: 'Card 卡片', path: '/eui/card' },
          { name: 'Avatar 头像', path: '/eui/avatar' },
          { name: 'Typography 排版', path: '/eui/typography' },
          { name: 'Kbd 键盘', path: '/eui/kbd' },
          { name: 'Separator 分隔线', path: '/eui/separator' },
          { name: 'Spinner 加载', path: '/eui/spinner' },
          { name: 'Empty 空状态', path: '/eui/empty' },
          { name: 'Label 标签', path: '/eui/label' },
          { name: 'AspectRatio 宽高比', path: '/eui/aspect-ratio' },
        ],
      },
      {
        title: '表单 Form',
        items: [
          { name: 'Input 输入框', path: '/eui/input' },
          { name: 'InputGroup 输入框组', path: '/eui/input-group' },
          { name: 'Mention 提及', path: '/eui/mention' },
          { name: 'Select 选择器', path: '/eui/select' },
          { name: 'Checkbox 复选框', path: '/eui/checkbox' },
          { name: 'Radio 单选框', path: '/eui/radio' },
          { name: 'Switch 开关', path: '/eui/switch' },
          { name: 'Slider 滑块', path: '/eui/slider' },
          { name: 'Rate 评分', path: '/eui/rate' },
          { name: 'DatePicker 日期', path: '/eui/date-picker' },
          { name: 'TimePicker 时间', path: '/eui/time-picker' },
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
          { name: 'Dialog 对话框', path: '/eui/dialog' },
          { name: 'Drawer 抽屉', path: '/eui/drawer' },
          { name: 'AlertDialog 警告对话框', path: '/eui/alert-dialog' },
          { name: 'Sheet 侧边面板', path: '/eui/sheet' },
          { name: 'Toast 轻提示', path: '/eui/toast' },
          { name: 'Tooltip 提示', path: '/eui/tooltip' },
          { name: 'Popover 气泡', path: '/eui/popover' },
          { name: 'HoverCard 悬浮卡片', path: '/eui/hover-card' },
          { name: 'ContextMenu 右键菜单', path: '/eui/context-menu' },
        ],
      },
      {
        title: '其他 Other',
        items: [
          { name: 'Accordion 手风琴', path: '/eui/accordion' },
          { name: 'Collapsible 折叠面板', path: '/eui/collapsible' },
          { name: 'Resizable 可调整面板', path: '/eui/resizable' },
          { name: 'ScrollArea 滚动区域', path: '/eui/scroll-area' },
          { name: 'InfiniteScroll 无限滚动', path: '/eui/infinite-scroll' },
          { name: 'Affix 固钉', path: '/eui/affix' },
          { name: 'Watermark 水印', path: '/eui/watermark' },
          { name: 'Image 图片', path: '/eui/image' },
          { name: 'Calendar 日历', path: '/eui/calendar' },
          { name: 'RangeCalendar 范围日历', path: '/eui/range-calendar' },
          { name: 'Transfer 穿梭框', path: '/eui/transfer' },
        ],
      },
      {
        title: '业务 Business',
        items: [
          { name: 'FormDialog 表单弹窗', path: '/eui/form-dialog' },
          { name: 'ConfirmDialog 确认弹窗', path: '/eui/confirm-dialog' },
          { name: 'DataPage 数据页', path: '/eui/data-page' },
          { name: 'AdminLayout 管理布局', path: '/eui/admin-layout' },
        ],
      },
      {
        title: 'Blocks 模板',
        items: [
          { name: 'Login 居中卡片', path: '/eui/blocks/login-01' },
          { name: 'Login 双栏图片', path: '/eui/blocks/login-02' },
          { name: 'Login 卡片图片', path: '/eui/blocks/login-04' },
          { name: 'OTP 验证码', path: '/eui/blocks/otp-01' },
        ],
      },
    ],
  },
  {
    key: 'ekit',
    label: 'EKit 工具',
    prefix: '/ekit',
    categories: [
      {
        title: '模块',
        items: [
          { name: '概览', path: '/ekit' },
          { name: 'request 请求', path: '/ekit/request' },
          { name: 'storage 存储', path: '/ekit/storage' },
          { name: 'validators 校验', path: '/ekit/validators' },
          { name: 'date 日期', path: '/ekit/date' },
          { name: 'hooks 组合式', path: '/ekit/hooks' },
        ],
      },
    ],
  },
  {
    key: 'eapi',
    label: 'EApi',
    prefix: '/eapi',
    categories: [
      {
        title: '模块',
        items: [
          { name: '概览', path: '/eapi' },
          { name: 'config 配置', path: '/eapi/config' },
          { name: 'database 数据库', path: '/eapi/database' },
          { name: 'security 安全', path: '/eapi/security' },
          { name: 'exceptions 异常', path: '/eapi/exceptions' },
          { name: 'response 响应', path: '/eapi/response' },
          { name: 'pagination 分页', path: '/eapi/pagination' },
          { name: 'cache 缓存', path: '/eapi/cache' },
          { name: 'dependencies 依赖', path: '/eapi/dependencies' },
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
          { name: 'dwy-eui', path: '/claude/skills/dwy-eui' },
          { name: 'dwy-ekit', path: '/claude/skills/dwy-ekit' },
          { name: 'dwy-eapi', path: '/claude/skills/dwy-eapi' },
          { name: 'dwy-cli-sync-local', path: '/claude/skills/dwy-cli-sync-local' },
          { name: 'dwy-dev-qa', path: '/claude/skills/dwy-dev-qa' },
          { name: 'dwy-git-commit', path: '/claude/skills/dwy-git-commit' },
          { name: 'dwy-pentest', path: '/claude/skills/dwy-pentest' },
          { name: 'dwy-publish', path: '/claude/skills/dwy-publish' },
          { name: 'dwy-tech-stack', path: '/claude/skills/dwy-tech-stack' },
        ],
      },
      {
        title: 'Rules · 项目结构',
        items: [
          { name: 'dwy-project-structure', path: '/claude/rules/dwy-project-structure' },
        ],
      },
      {
        title: 'Rules · 开发流程与提交',
        items: [
          { name: 'dwy-tdd-development', path: '/claude/rules/dwy-tdd-development' },
        ],
      },
      {
        title: 'Rules · 安全',
        items: [
          { name: 'dwy-server-security', path: '/claude/rules/dwy-server-security' },
        ],
      },
      {
        title: 'Rules · 数据库与基础设施',
        items: [
          { name: 'dwy-db-migration', path: '/claude/rules/dwy-db-migration' },
          { name: 'dwy-postgres', path: '/claude/rules/dwy-postgres' },
          { name: 'dwy-redis', path: '/claude/rules/dwy-redis' },
        ],
      },
      {
        title: 'Rules · Python 后端',
        items: [
          { name: 'dwy-python-core', path: '/claude/rules/dwy-python-core' },
          { name: 'dwy-python-backend', path: '/claude/rules/dwy-python-backend' },
          { name: 'dwy-python-base-lib', path: '/claude/rules/dwy-python-base-lib' },
          { name: 'dwy-python-testing', path: '/claude/rules/dwy-python-testing' },
        ],
      },
      {
        title: 'Rules · Vue 前端',
        items: [
          { name: 'dwy-vue-core', path: '/claude/rules/dwy-vue-core' },
          { name: 'dwy-vue-base-lib', path: '/claude/rules/dwy-vue-base-lib' },
          { name: 'dwy-vue-pinia', path: '/claude/rules/dwy-vue-pinia' },
          { name: 'dwy-vue-testing', path: '/claude/rules/dwy-vue-testing' },
        ],
      },
      {
        title: 'Rules · Flutter 移动端',
        items: [
          { name: 'dwy-flutter-core', path: '/claude/rules/dwy-flutter-core' },
          { name: 'dwy-flutter-network', path: '/claude/rules/dwy-flutter-network' },
          { name: 'dwy-flutter-router', path: '/claude/rules/dwy-flutter-router' },
          { name: 'dwy-flutter-testing', path: '/claude/rules/dwy-flutter-testing' },
        ],
      },
      {
        title: 'Rules · 基础设施',
        items: [
          { name: 'dwy-docker-spec', path: '/claude/rules/dwy-docker-spec' },
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
