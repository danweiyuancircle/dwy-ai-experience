import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: () => import('./views/HomeView.vue') },

    // EUI Components (existing demos, prefixed with /eui)
    { path: '/eui', component: () => import('./views/EuiOverview.vue') },
    { path: '/eui/button', component: () => import('./views/ButtonDemo.vue') },
    { path: '/eui/input', component: () => import('./views/InputDemo.vue') },
    { path: '/eui/select', component: () => import('./views/SelectDemo.vue') },
    { path: '/eui/checkbox-radio', component: () => import('./views/CheckboxRadioDemo.vue') },
    { path: '/eui/switch', component: () => import('./views/SwitchDemo.vue') },
    { path: '/eui/form', component: () => import('./views/FormDemo.vue') },
    { path: '/eui/table', component: () => import('./views/TableDemo.vue') },
    { path: '/eui/dialog-drawer', component: () => import('./views/DialogDrawerDemo.vue') },
    { path: '/eui/toast', component: () => import('./views/ToastDemo.vue') },
    { path: '/eui/tabs', component: () => import('./views/TabsDemo.vue') },
    { path: '/eui/menu', component: () => import('./views/MenuDemo.vue') },
    { path: '/eui/card', component: () => import('./views/CardDemo.vue') },
    { path: '/eui/alert-badge', component: () => import('./views/AlertBadgeDemo.vue') },
    { path: '/eui/tooltip-popover', component: () => import('./views/TooltipPopoverDemo.vue') },
    { path: '/eui/dropdown', component: () => import('./views/DropdownDemo.vue') },
    { path: '/eui/pagination', component: () => import('./views/PaginationDemo.vue') },
    { path: '/eui/breadcrumb', component: () => import('./views/BreadcrumbDemo.vue') },
    { path: '/eui/tags-input', component: () => import('./views/TagsInputDemo.vue') },
    { path: '/eui/date-time', component: () => import('./views/DateTimeDemo.vue') },
    { path: '/eui/tree', component: () => import('./views/TreeDemo.vue') },
    { path: '/eui/upload', component: () => import('./views/UploadDemo.vue') },
    { path: '/eui/progress', component: () => import('./views/ProgressDemo.vue') },
    { path: '/eui/accordion', component: () => import('./views/AccordionDemo.vue') },
    { path: '/eui/stepper', component: () => import('./views/StepperDemo.vue') },
    { path: '/eui/carousel', component: () => import('./views/CarouselDemo.vue') },
    { path: '/eui/avatar', component: () => import('./views/AvatarDemo.vue') },
    { path: '/eui/skeleton', component: () => import('./views/SkeletonDemo.vue') },
    { path: '/eui/slider', component: () => import('./views/SliderDemo.vue') },
    { path: '/eui/rate', component: () => import('./views/RateDemo.vue') },
    { path: '/eui/transfer', component: () => import('./views/TransferDemo.vue') },
    { path: '/eui/descriptions', component: () => import('./views/DescriptionsDemo.vue') },
    { path: '/eui/timeline', component: () => import('./views/TimelineDemo.vue') },
    { path: '/eui/statistic', component: () => import('./views/StatisticDemo.vue') },
    { path: '/eui/business', component: () => import('./views/BusinessDemo.vue') },
    { path: '/eui/misc', component: () => import('./views/MiscDemo.vue') },

    // Core
    { path: '/core', component: () => import('./views/core/CoreOverview.vue') },
    { path: '/core/request', component: () => import('./views/core/RequestDoc.vue') },
    { path: '/core/storage', component: () => import('./views/core/StorageDoc.vue') },
    { path: '/core/validators', component: () => import('./views/core/ValidatorsDoc.vue') },
    { path: '/core/date', component: () => import('./views/core/DateDoc.vue') },
    { path: '/core/hooks', component: () => import('./views/core/HooksDoc.vue') },

    // Backend
    { path: '/backend', component: () => import('./views/backend/BackendOverview.vue') },
    { path: '/backend/config', component: () => import('./views/backend/ConfigDoc.vue') },
    { path: '/backend/database', component: () => import('./views/backend/DatabaseDoc.vue') },
    { path: '/backend/security', component: () => import('./views/backend/SecurityDoc.vue') },
    { path: '/backend/exceptions', component: () => import('./views/backend/ExceptionsDoc.vue') },
    { path: '/backend/response', component: () => import('./views/backend/ResponseDoc.vue') },
    { path: '/backend/pagination', component: () => import('./views/backend/PaginationDoc.vue') },
    { path: '/backend/cache', component: () => import('./views/backend/CacheDoc.vue') },
    { path: '/backend/dependencies', component: () => import('./views/backend/DependenciesDoc.vue') },

    // CLI
    { path: '/cli', component: () => import('./views/cli/CliOverview.vue') },
    { path: '/cli/create-dwy', component: () => import('./views/cli/CreateDwyDoc.vue') },

    // Claude Code
    { path: '/claude', component: () => import('./views/claude/ClaudeOverview.vue') },
    { path: '/claude/skills/:name', component: () => import('./views/claude/SkillDoc.vue') },
    { path: '/claude/rules/:name', component: () => import('./views/claude/RuleDoc.vue') },
    { path: '/claude/hooks/:name', component: () => import('./views/claude/HookDoc.vue') },
    { path: '/claude/settings', component: () => import('./views/claude/SettingsDoc.vue') },
  ],
})

export default router
