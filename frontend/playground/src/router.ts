import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import ButtonDemo from './views/ButtonDemo.vue'
import InputDemo from './views/InputDemo.vue'
import SelectDemo from './views/SelectDemo.vue'
import CheckboxRadioDemo from './views/CheckboxRadioDemo.vue'
import SwitchDemo from './views/SwitchDemo.vue'
import FormDemo from './views/FormDemo.vue'
import TableDemo from './views/TableDemo.vue'
import DialogDrawerDemo from './views/DialogDrawerDemo.vue'
import ToastDemo from './views/ToastDemo.vue'
import TabsDemo from './views/TabsDemo.vue'
import MenuDemo from './views/MenuDemo.vue'
import CardDemo from './views/CardDemo.vue'
import AlertBadgeDemo from './views/AlertBadgeDemo.vue'
import TooltipPopoverDemo from './views/TooltipPopoverDemo.vue'
import DropdownDemo from './views/DropdownDemo.vue'
import PaginationDemo from './views/PaginationDemo.vue'
import BreadcrumbDemo from './views/BreadcrumbDemo.vue'
import TagsInputDemo from './views/TagsInputDemo.vue'
import DateTimeDemo from './views/DateTimeDemo.vue'
import TreeDemo from './views/TreeDemo.vue'
import UploadDemo from './views/UploadDemo.vue'
import ProgressDemo from './views/ProgressDemo.vue'
import AccordionDemo from './views/AccordionDemo.vue'
import StepperDemo from './views/StepperDemo.vue'
import CarouselDemo from './views/CarouselDemo.vue'
import AvatarDemo from './views/AvatarDemo.vue'
import SkeletonDemo from './views/SkeletonDemo.vue'
import SliderDemo from './views/SliderDemo.vue'
import RateDemo from './views/RateDemo.vue'
import TransferDemo from './views/TransferDemo.vue'
import DescriptionsDemo from './views/DescriptionsDemo.vue'
import TimelineDemo from './views/TimelineDemo.vue'
import StatisticDemo from './views/StatisticDemo.vue'
import BusinessDemo from './views/BusinessDemo.vue'
import MiscDemo from './views/MiscDemo.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/button', component: ButtonDemo },
    { path: '/input', component: InputDemo },
    { path: '/select', component: SelectDemo },
    { path: '/checkbox-radio', component: CheckboxRadioDemo },
    { path: '/switch', component: SwitchDemo },
    { path: '/form', component: FormDemo },
    { path: '/table', component: TableDemo },
    { path: '/dialog-drawer', component: DialogDrawerDemo },
    { path: '/toast', component: ToastDemo },
    { path: '/tabs', component: TabsDemo },
    { path: '/menu', component: MenuDemo },
    { path: '/card', component: CardDemo },
    { path: '/alert-badge', component: AlertBadgeDemo },
    { path: '/tooltip-popover', component: TooltipPopoverDemo },
    { path: '/dropdown', component: DropdownDemo },
    { path: '/pagination', component: PaginationDemo },
    { path: '/breadcrumb', component: BreadcrumbDemo },
    { path: '/tags-input', component: TagsInputDemo },
    { path: '/date-time', component: DateTimeDemo },
    { path: '/tree', component: TreeDemo },
    { path: '/upload', component: UploadDemo },
    { path: '/progress', component: ProgressDemo },
    { path: '/accordion', component: AccordionDemo },
    { path: '/stepper', component: StepperDemo },
    { path: '/carousel', component: CarouselDemo },
    { path: '/avatar', component: AvatarDemo },
    { path: '/skeleton', component: SkeletonDemo },
    { path: '/slider', component: SliderDemo },
    { path: '/rate', component: RateDemo },
    { path: '/transfer', component: TransferDemo },
    { path: '/descriptions', component: DescriptionsDemo },
    { path: '/timeline', component: TimelineDemo },
    { path: '/statistic', component: StatisticDemo },
    { path: '/business', component: BusinessDemo },
    { path: '/misc', component: MiscDemo },
  ],
})

export default router
