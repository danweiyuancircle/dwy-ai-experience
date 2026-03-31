<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const weeklySchedule = [
  { day: 0, startHour: 8, endHour: 10, title: '高等数学' },
  { day: 0, startHour: 10, endHour: 12, title: '大学英语' },
  { day: 0, startHour: 14, endHour: 16, title: '数据结构' },
  { day: 1, startHour: 8, endHour: 10, title: '线性代数' },
  { day: 1, startHour: 10, endHour: 12, title: '计算机网络' },
  { day: 1, startHour: 14, endHour: 15, title: '体育课' },
  { day: 2, startHour: 8, endHour: 10, title: '高等数学' },
  { day: 2, startHour: 10, endHour: 12, title: '操作系统' },
  { day: 2, startHour: 14, endHour: 16, title: '软件工程' },
  { day: 2, startHour: 16, endHour: 18, title: '实验课' },
  { day: 3, startHour: 8, endHour: 10, title: '大学英语' },
  { day: 3, startHour: 10, endHour: 12, title: '数据库原理' },
  { day: 3, startHour: 14, endHour: 16, title: '数据结构' },
  { day: 4, startHour: 8, endHour: 10, title: '线性代数' },
  { day: 4, startHour: 10, endHour: 12, title: '计算机网络' },
  { day: 4, startHour: 14, endHour: 17, title: '课程设计' },
]

const workSchedule = [
  { day: 0, startHour: 9, endHour: 10, title: '晨会', color: '#3b82f6' },
  { day: 0, startHour: 10, endHour: 12, title: '需求评审', color: '#8b5cf6' },
  { day: 0, startHour: 14, endHour: 17, title: '编码开发', color: '#10b981' },
  { day: 1, startHour: 9, endHour: 10, title: '晨会', color: '#3b82f6' },
  { day: 1, startHour: 10, endHour: 12, title: '编码开发', color: '#10b981' },
  { day: 1, startHour: 14, endHour: 16, title: '代码评审', color: '#f59e0b' },
  { day: 2, startHour: 9, endHour: 10, title: '晨会', color: '#3b82f6' },
  { day: 2, startHour: 10, endHour: 12, title: '编码开发', color: '#10b981' },
  { day: 2, startHour: 14, endHour: 15, title: '周中总结', color: '#ef4444' },
  { day: 2, startHour: 15, endHour: 17, title: '编码开发', color: '#10b981' },
  { day: 3, startHour: 9, endHour: 10, title: '晨会', color: '#3b82f6' },
  { day: 3, startHour: 10, endHour: 12, title: '技术分享', color: '#ec4899' },
  { day: 3, startHour: 14, endHour: 17, title: '编码开发', color: '#10b981' },
  { day: 4, startHour: 9, endHour: 10, title: '晨会', color: '#3b82f6' },
  { day: 4, startHour: 10, endHour: 12, title: '编码开发', color: '#10b981' },
  { day: 4, startHour: 14, endHour: 16, title: '测试验收', color: '#f97316' },
  { day: 4, startHour: 16, endHour: 17, title: '周报总结', color: '#ef4444' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'course', label: '课程表' },
  { id: 'work', label: '工作日程' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'data', type: 'TimetableItem[]', default: '[]', description: '时间表数据，每项包含 day、startHour、endHour、title、color' },
  { name: 'startHour', type: 'number', default: '8', description: '起始小时（24 小时制）' },
  { name: 'endHour', type: 'number', default: '22', description: '结束小时（24 小时制）' },
  { name: 'days', type: 'string[]', default: "['周一', ..., '周日']", description: '列头显示的天数名称数组' },
]

const slotsData = [
  { name: 'default', description: '默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="TimetableGrid 时间表"
    description="基于网格的时间表组件，适用于课程表、日程安排等按时间段和天数展示的场景，支持自定义颜色和时间范围。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于高校课程表展示、员工排班表、会议室日程安排等需要按天和时间段组织数据的场景。通过 CSS Grid 实现精确的时间段定位，每个事项按实际时间跨度占据对应的网格空间。</p>
    </section>

    <section id="course">
      <DemoBlock
        title="课程表"
        description="大学课程表，使用默认颜色主题，工作日 5 天"
        code='<ETimetableGrid
  :data="weeklySchedule"
  :start-hour="8"
  :end-hour="18"
  :days="[&apos;周一&apos;, &apos;周二&apos;, &apos;周三&apos;, &apos;周四&apos;, &apos;周五&apos;]"
/>'
      >
        <ETimetableGrid
          :data="weeklySchedule"
          :start-hour="8"
          :end-hour="18"
          :days="['周一', '周二', '周三', '周四', '周五']"
        />
      </DemoBlock>
    </section>

    <section id="work">
      <DemoBlock
        title="工作日程"
        description="工作周日程安排，使用自定义颜色区分不同类型事项"
        code='<ETimetableGrid
  :data="workSchedule"
  :start-hour="9"
  :end-hour="18"
  :days="[&apos;周一&apos;, &apos;周二&apos;, &apos;周三&apos;, &apos;周四&apos;, &apos;周五&apos;]"
/>'
      >
        <ETimetableGrid
          :data="workSchedule"
          :start-hour="9"
          :end-hour="18"
          :days="['周一', '周二', '周三', '周四', '周五']"
        />
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
