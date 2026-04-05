// Utils
export { cn } from './utils/cn'

// Types
export type * from './types'

// Composables
export {
  useFormField,
  FORM_ITEM_INJECTION_KEY,
  useConfigProvider,
  CONFIG_PROVIDER_KEY,
  useTheme,
  useMessage,
  useNotification,
  useMessageBox,
} from './composables'

// Components
export { EConfigProvider } from './components/config-provider'
export { EButton, buttonVariants } from './components/button'
export type { EButtonProps, ButtonVariants } from './components/button'
export { EBadge, badgeVariants } from './components/badge'
export type { EBadgeProps, BadgeVariants } from './components/badge'
export { EAlert, alertVariants } from './components/alert'
export type { EAlertProps, EAlertEmits, AlertVariants } from './components/alert'
export { ECard } from './components/card'
export type { ECardProps } from './components/card'
export { ETooltip } from './components/tooltip'
export type { ETooltipProps } from './components/tooltip'
export { EPopover } from './components/popover'
export type { EPopoverProps, EPopoverEmits } from './components/popover'
export { EInput } from './components/input'
export type { EInputProps, EInputEmits } from './components/input'
export { ECheckbox } from './components/checkbox'
export type { ECheckboxProps, ECheckboxEmits } from './components/checkbox'
export { ERadio } from './components/radio'
export type { ERadioProps, ERadioEmits } from './components/radio'
export { ESwitch } from './components/switch'
export type { ESwitchProps, ESwitchEmits } from './components/switch'
export { ESelect } from './components/select'
export type { ESelectProps, ESelectEmits } from './components/select'
export { ETagsInput } from './components/tags-input'
export type { ETagsInputProps, ETagsInputEmits } from './components/tags-input'
export { EDropdown } from './components/dropdown'
export type { EDropdownProps, EDropdownEmits, DropdownMenuItem } from './components/dropdown'
export { ETabs } from './components/tabs'
export type { ETabsProps, ETabsEmits, TabItem } from './components/tabs'
export { EBreadcrumb } from './components/breadcrumb'
export type { EBreadcrumbProps, BreadcrumbItem } from './components/breadcrumb'
export { EPagination } from './components/pagination'
export type { EPaginationProps, EPaginationEmits } from './components/pagination'
export { EDialog } from './components/dialog'
export type { EDialogProps, EDialogEmits } from './components/dialog'
export { EDrawer } from './components/drawer'
export type { EDrawerProps, EDrawerEmits, DrawerDirection } from './components/drawer'
export { EToast, useToast } from './components/toast'
export type { EToastProps } from './components/toast'
export { EForm, EFormItem } from './components/form'
export type { EFormProps, EFormEmits, EFormExpose, EFormItemProps } from './components/form'
export { ETable } from './components/table'
export type { ETableProps, ETableEmits } from './components/table'
export { EMenu } from './components/menu'
export type { EMenuProps, EMenuEmits } from './components/menu'
export { ETextarea } from './components/textarea'
export type { ETextareaProps, ETextareaEmits } from './components/textarea'
export { ENumberField } from './components/number-field'
export type { ENumberFieldProps, ENumberFieldEmits } from './components/number-field'
export { EAccordion } from './components/accordion'
export type { EAccordionProps, EAccordionEmits, AccordionItemOption } from './components/accordion'
export { ECollapsible } from './components/collapsible'
export type { ECollapsibleProps, ECollapsibleEmits } from './components/collapsible'
export { ESheet } from './components/sheet'
export type { ESheetProps, ESheetEmits } from './components/sheet'
export { ESkeleton } from './components/skeleton'
export type { ESkeletonProps } from './components/skeleton'
export { EProgress } from './components/progress'
export type { EProgressProps } from './components/progress'

// P1 Components
export { ECombobox } from './components/combobox'
export type { EComboboxProps, EComboboxEmits } from './components/combobox'
export {
  ECommand,
  ECommandInput,
  ECommandList,
  ECommandEmpty,
  ECommandGroup,
  ECommandItem,
  ECommandSeparator,
  ECommandShortcut,
  useCommand,
} from './components/command'
export { EDatePicker } from './components/date-picker'
export type { EDatePickerProps, EDatePickerEmits, DatePickerType, DatePickerShortcut } from './components/date-picker'
export { EStepper } from './components/stepper'
export type { EStepperProps, EStepperEmits, StepperItem } from './components/stepper'
export { ECarousel, ECarouselItem } from './components/carousel'
export type { ECarouselProps, ECarouselEmits } from './components/carousel'
export { EImage } from './components/image'
export type { EImageProps } from './components/image'
export { ETimePicker } from './components/time-picker'
export type { ETimePickerProps, ETimePickerEmits } from './components/time-picker'
export { EUpload } from './components/upload'
export type { EUploadProps, EUploadEmits, UploadFile } from './components/upload'
export { ETree } from './components/tree'
export type { ETreeProps, ETreeEmits, TreeNode } from './components/tree'
export { ETreeSelect } from './components/tree-select'
export type { ETreeSelectProps, ETreeSelectEmits } from './components/tree-select'
export { ECascader } from './components/cascader'
export type { ECascaderProps, ECascaderEmits, CascaderOption } from './components/cascader'

// P2 Components
export { EContextMenu } from './components/context-menu'
export type { EContextMenuProps, EContextMenuEmits, ContextMenuItem } from './components/context-menu'
export {
  ENavigationMenu,
  ENavigationMenuList,
  ENavigationMenuItem,
  ENavigationMenuTrigger,
  ENavigationMenuContent,
  ENavigationMenuLink,
  ENavigationMenuViewport,
} from './components/navigation-menu'
export {
  EMenubar,
  EMenubarMenu,
  EMenubarTrigger,
  EMenubarContent,
  EMenubarItem,
  EMenubarSeparator,
  EMenubarCheckboxItem,
  EMenubarRadioGroup,
  EMenubarRadioItem,
  EMenubarSub,
  EMenubarSubTrigger,
  EMenubarSubContent,
} from './components/menubar'
export { EHoverCard } from './components/hover-card'
export type { EHoverCardProps } from './components/hover-card'
export {
  EResizablePanelGroup,
  EResizablePanel,
  EResizableHandle,
} from './components/resizable'
export type { EResizablePanelGroupProps, EResizablePanelProps, EResizableHandleProps } from './components/resizable'
export { EScrollArea } from './components/scroll-area'
export type { EScrollAreaProps } from './components/scroll-area'
export { EChartContainer } from './components/chart'
export type { EChartContainerProps, ChartConfig } from './components/chart'
export { ERangeCalendar } from './components/range-calendar'
export type { ERangeCalendarProps, ERangeCalendarEmits } from './components/range-calendar'
export { ECalendar } from './components/calendar'
export type { ECalendarProps, ECalendarEmits } from './components/calendar'
export { EAutocomplete } from './components/autocomplete'
export type { EAutocompleteProps, EAutocompleteEmits, AutocompleteOption } from './components/autocomplete'
export { ETransfer } from './components/transfer'
export type { ETransferProps, ETransferEmits, TransferItem } from './components/transfer'
export { EVirtualTable } from './components/virtual-table'
export type { EVirtualTableProps, EVirtualTableEmits, VirtualTableColumn } from './components/virtual-table'
export { EDescriptions } from './components/descriptions'
export type { EDescriptionsProps, DescriptionItem } from './components/descriptions'
export { ETimeline } from './components/timeline'
export type { ETimelineProps, TimelineItem } from './components/timeline'
export { EStatistic } from './components/statistic'
export type { EStatisticProps } from './components/statistic'
export { ERate } from './components/rate'
export type { ERateProps, ERateEmits } from './components/rate'
export { EColorPicker } from './components/color-picker'
export type { EColorPickerProps, EColorPickerEmits } from './components/color-picker'
export { EInfiniteScroll } from './components/infinite-scroll'
export type { EInfiniteScrollProps, EInfiniteScrollEmits } from './components/infinite-scroll'
export { EAffix } from './components/affix'
export type { EAffixProps } from './components/affix'
export { EWatermark } from './components/watermark'
export type { EWatermarkProps } from './components/watermark'
export { EMention } from './components/mention'
export type { EMentionProps, EMentionEmits, MentionOption } from './components/mention'

// P3 Components
export { EButtonGroup, buttonGroupVariants } from './components/button-group'
export type { EButtonGroupProps, ButtonGroupVariants } from './components/button-group'
export { EAlertDialog } from './components/alert-dialog'
export type { EAlertDialogProps, EAlertDialogEmits } from './components/alert-dialog'
export { EAvatar } from './components/avatar'
export type { EAvatarProps } from './components/avatar'
export { EEmpty } from './components/empty'
export type { EEmptyProps } from './components/empty'
export { EAspectRatio } from './components/aspect-ratio'
export type { EAspectRatioProps } from './components/aspect-ratio'
export { EToggle, toggleVariants } from './components/toggle'
export type { EToggleProps, EToggleEmits, ToggleVariants } from './components/toggle'
export { EToggleGroup } from './components/toggle-group'
export type { EToggleGroupProps, EToggleGroupEmits } from './components/toggle-group'
export { ESlider } from './components/slider'
export type { ESliderProps, ESliderEmits } from './components/slider'
export { ESpinner } from './components/spinner'
export type { ESpinnerProps } from './components/spinner'
export { ELabel } from './components/label'
export type { ELabelProps } from './components/label'
export { EKbd } from './components/kbd'
export type { EKbdProps } from './components/kbd'
export { ESeparator } from './components/separator'
export type { ESeparatorProps } from './components/separator'
export { ETypography } from './components/typography'
export type { ETypographyProps, TypographyVariant } from './components/typography'
export { EItem, itemVariants } from './components/item'
export type { EItemProps, ItemVariants } from './components/item'
export { EField, fieldVariants } from './components/field'
export type { EFieldProps, FieldVariants } from './components/field'
export { EInputGroup, EInputGroupAddon, inputGroupAddonVariants } from './components/input-group'
export type { EInputGroupProps, EInputGroupAddonProps, InputGroupVariants } from './components/input-group'
export { EInputOTP } from './components/input-otp'
export type { EInputOTPProps, EInputOTPEmits } from './components/input-otp'
export { EPinInput } from './components/pin-input'
export type { EPinInputProps, EPinInputEmits } from './components/pin-input'
export { ENativeSelect } from './components/native-select'
export type { ENativeSelectProps, ENativeSelectEmits, SelectOption } from './components/native-select'

// Business Components
export { EDataPage } from './components/data-page'
export type { EDataPageProps, FetchParams, FetchResult } from './components/data-page'
export { EFormDialog } from './components/form-dialog'
export type { EFormDialogProps, EFormDialogEmits } from './components/form-dialog'
export { EConfirmDialog } from './components/confirm-dialog'
export type { EConfirmDialogProps, EConfirmDialogEmits, ConfirmDialogType } from './components/confirm-dialog'
export { EAdminLayout } from './components/admin-layout'
export type { EAdminLayoutProps, EAdminLayoutEmits } from './components/admin-layout'
export { ELoginLayout } from './components/login-layout'
export type { ELoginLayoutProps } from './components/login-layout'
export { EAIChat } from './components/ai-chat'
export type { EAIChatProps, EAIChatEmits, ChatMessage } from './components/ai-chat'
export { ETimetableGrid } from './components/timetable-grid'
export type { ETimetableGridProps, TimetableItem } from './components/timetable-grid'

// Vue plugin
import type { App } from 'vue'
import { EConfigProvider } from './components/config-provider'
import { EButton } from './components/button'
import { EBadge } from './components/badge'
import { EAlert } from './components/alert'
import { ECard } from './components/card'
import { ETooltip } from './components/tooltip'
import { EPopover } from './components/popover'
import { EInput } from './components/input'
import { ECheckbox } from './components/checkbox'
import { ERadio } from './components/radio'
import { ESwitch } from './components/switch'
import { ESelect } from './components/select'
import { ETagsInput } from './components/tags-input'
import { EDropdown } from './components/dropdown'
import { ETabs } from './components/tabs'
import { EBreadcrumb } from './components/breadcrumb'
import { EPagination } from './components/pagination'
import { EDialog } from './components/dialog'
import { EDrawer } from './components/drawer'
import { EToast } from './components/toast'
import { EForm, EFormItem } from './components/form'
import { ETable } from './components/table'
import { EMenu } from './components/menu'
import { ETextarea } from './components/textarea'
import { ENumberField } from './components/number-field'
import { EAccordion } from './components/accordion'
import { ECollapsible } from './components/collapsible'
import { ESheet } from './components/sheet'
import { ESkeleton } from './components/skeleton'
import { EProgress } from './components/progress'
import { ECombobox } from './components/combobox'
import {
  ECommand,
  ECommandInput,
  ECommandList,
  ECommandEmpty,
  ECommandGroup,
  ECommandItem,
  ECommandSeparator,
  ECommandShortcut,
} from './components/command'
import { EDatePicker } from './components/date-picker'
import { EStepper } from './components/stepper'
import { ECarousel, ECarouselItem } from './components/carousel'
import { EImage } from './components/image'
import { ETimePicker } from './components/time-picker'
import { EUpload } from './components/upload'
import { ETree } from './components/tree'
import { ETreeSelect } from './components/tree-select'
import { ECascader } from './components/cascader'
import { EContextMenu } from './components/context-menu'
import {
  ENavigationMenu,
  ENavigationMenuList,
  ENavigationMenuItem,
  ENavigationMenuTrigger,
  ENavigationMenuContent,
  ENavigationMenuLink,
  ENavigationMenuViewport,
} from './components/navigation-menu'
import {
  EMenubar,
  EMenubarMenu,
  EMenubarTrigger,
  EMenubarContent,
  EMenubarItem,
  EMenubarSeparator,
  EMenubarCheckboxItem,
  EMenubarRadioGroup,
  EMenubarRadioItem,
  EMenubarSub,
  EMenubarSubTrigger,
  EMenubarSubContent,
} from './components/menubar'
import { EHoverCard } from './components/hover-card'
import { EResizablePanelGroup, EResizablePanel, EResizableHandle } from './components/resizable'
import { EScrollArea } from './components/scroll-area'
import { EChartContainer } from './components/chart'
import { ERangeCalendar } from './components/range-calendar'
import { ECalendar } from './components/calendar'
import { EAutocomplete } from './components/autocomplete'
import { ETransfer } from './components/transfer'
import { EVirtualTable } from './components/virtual-table'
import { EDescriptions } from './components/descriptions'
import { ETimeline } from './components/timeline'
import { EStatistic } from './components/statistic'
import { ERate } from './components/rate'
import { EColorPicker } from './components/color-picker'
import { EInfiniteScroll } from './components/infinite-scroll'
import { EAffix } from './components/affix'
import { EWatermark } from './components/watermark'
import { EMention } from './components/mention'
import { EButtonGroup } from './components/button-group'
import { EAlertDialog } from './components/alert-dialog'
import { EAvatar } from './components/avatar'
import { EEmpty } from './components/empty'
import { EAspectRatio } from './components/aspect-ratio'
import { EToggle } from './components/toggle'
import { EToggleGroup } from './components/toggle-group'
import { ESlider } from './components/slider'
import { ESpinner } from './components/spinner'
import { ELabel } from './components/label'
import { EKbd } from './components/kbd'
import { ESeparator } from './components/separator'
import { ETypography } from './components/typography'
import { EItem } from './components/item'
import { EField } from './components/field'
import { EInputGroup, EInputGroupAddon } from './components/input-group'
import { EInputOTP } from './components/input-otp'
import { EPinInput } from './components/pin-input'
import { ENativeSelect } from './components/native-select'
import { EDataPage } from './components/data-page'
import { EFormDialog } from './components/form-dialog'
import { EConfirmDialog } from './components/confirm-dialog'
import { EAdminLayout } from './components/admin-layout'
import { ELoginLayout } from './components/login-layout'
import { EAIChat } from './components/ai-chat'
import { ETimetableGrid } from './components/timetable-grid'

const components: Record<string, any> = {
  EConfigProvider,
  EButton,
  EBadge,
  EAlert,
  ECard,
  ETooltip,
  EPopover,
  EInput,
  ECheckbox,
  ERadio,
  ESwitch,
  ESelect,
  ETagsInput,
  EDropdown,
  ETabs,
  EBreadcrumb,
  EPagination,
  EDialog,
  EDrawer,
  EToast,
  EForm,
  EFormItem,
  ETable,
  EMenu,
  ETextarea,
  ENumberField,
  EAccordion,
  ECollapsible,
  ESheet,
  ESkeleton,
  EProgress,
  ECombobox,
  ECommand,
  ECommandInput,
  ECommandList,
  ECommandEmpty,
  ECommandGroup,
  ECommandItem,
  ECommandSeparator,
  ECommandShortcut,
  EDatePicker,
  EStepper,
  ECarousel,
  ECarouselItem,
  EImage,
  ETimePicker,
  EUpload,
  ETree,
  ETreeSelect,
  ECascader,
  EContextMenu,
  ENavigationMenu,
  ENavigationMenuList,
  ENavigationMenuItem,
  ENavigationMenuTrigger,
  ENavigationMenuContent,
  ENavigationMenuLink,
  ENavigationMenuViewport,
  EMenubar,
  EMenubarMenu,
  EMenubarTrigger,
  EMenubarContent,
  EMenubarItem,
  EMenubarSeparator,
  EMenubarCheckboxItem,
  EMenubarRadioGroup,
  EMenubarRadioItem,
  EMenubarSub,
  EMenubarSubTrigger,
  EMenubarSubContent,
  EHoverCard,
  EResizablePanelGroup,
  EResizablePanel,
  EResizableHandle,
  EScrollArea,
  EChartContainer,
  ERangeCalendar,
  ECalendar,
  EAutocomplete,
  ETransfer,
  EVirtualTable,
  EDescriptions,
  ETimeline,
  EStatistic,
  ERate,
  EColorPicker,
  EInfiniteScroll,
  EAffix,
  EWatermark,
  EMention,
  EButtonGroup,
  EAlertDialog,
  EAvatar,
  EEmpty,
  EAspectRatio,
  EToggle,
  EToggleGroup,
  ESlider,
  ESpinner,
  ELabel,
  EKbd,
  ESeparator,
  ETypography,
  EItem,
  EField,
  EInputGroup,
  EInputGroupAddon,
  EInputOTP,
  EPinInput,
  ENativeSelect,
  EDataPage,
  EFormDialog,
  EConfirmDialog,
  EAdminLayout,
  ELoginLayout,
  EAIChat,
  ETimetableGrid,
}

export default {
  install(app: App) {
    for (const [name, component] of Object.entries(components)) {
      app.component(name, component)
    }
  },
}
