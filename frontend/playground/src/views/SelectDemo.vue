<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basic = ref('')
const grouped = ref('')
const clearable = ref('vue')
const disabled = ref('react')
const sizeSm = ref('')
const sizeLg = ref('')
const searchValue = ref('')
const multiValue = ref<string[]>([])
const collapseValue = ref<string[]>([])

const fruits = [
  { label: '苹果', value: 'apple' },
  { label: '香蕉', value: 'banana' },
  { label: '橙子', value: 'orange' },
  { label: '草莓', value: 'strawberry' },
  { label: '葡萄', value: 'grape' },
]

const frameworks = [
  {
    label: '前端框架',
    options: [
      { label: 'Vue 3', value: 'vue' },
      { label: 'React', value: 'react' },
      { label: 'Angular', value: 'angular' },
    ],
  },
  {
    label: '后端框架',
    options: [
      { label: 'FastAPI', value: 'fastapi' },
      { label: 'Django', value: 'django' },
      { label: 'Express', value: 'express' },
    ],
  },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'grouped', label: '分组选项' },
  { id: 'clearable', label: '可清除' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'sizes', label: '尺寸变体' },
  { id: 'filterable', label: '可搜索' },
  { id: 'multiple', label: '多选模式' },
  { id: 'collapse-tags', label: '标签折叠' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: "string | number | (string | number)[]", description: '绑定值，多选时为数组' },
  { name: 'options', type: "Option[] | GroupedOption[]", description: '选项数据，支持平铺或分组格式' },
  { name: 'placeholder', type: 'string', description: '占位提示文字' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '选择器尺寸' },
  { name: 'clearable', type: 'boolean', default: 'false', description: '是否可清空' },
  { name: 'valueKey', type: 'string', description: '自定义 value 字段名' },
  { name: 'labelKey', type: 'string', description: '自定义 label 字段名' },
  { name: 'filterable', type: 'boolean', default: 'false', description: '是否可搜索过滤' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否允许多选' },
  { name: 'collapseTags', type: 'boolean', default: 'false', description: '多选时折叠标签，显示 "+N"' },
  { name: 'remote', type: 'boolean', default: 'false', description: '是否远程搜索模式（需配合 remoteMethod）' },
  { name: 'remoteMethod', type: '(query: string) => Promise<void>', description: '远程搜索方法' },
  { name: 'loading', type: 'boolean', default: 'false', description: '是否显示加载状态（远程模式）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发' },
  { name: 'visible-change', params: '(visible: boolean)', description: '下拉菜单显示/隐藏时触发' },
]

const slotsData = [
  { name: 'default', description: '自定义选项内容' },
]
</script>

<template>
  <ComponentDoc
    title="Select 选择器"
    description="下拉选择组件，支持单选、多选、分组选项、可搜索、可清除、禁用等特性。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于从一组预定义选项中选择一个或多个值的场景，如表单中的角色选择、状态筛选、城市选择等。选项较多时可启用 filterable 搜索过滤，远程数据源可使用 remote + remoteMethod 实现异步搜索。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="最简单的下拉选择"
        code='<ESelect v-model="value" :options="options" placeholder="请选择水果" />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="basic" :options="fruits" placeholder="请选择水果" />
          <p class="text-sm text-muted-foreground">当前值：{{ basic || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="grouped">
      <DemoBlock
        title="分组选项"
        description="使用 GroupedOption 格式的 options 实现分组"
        code='<ESelect v-model="value" :options="groupedOptions" placeholder="请选择框架" />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="grouped" :options="frameworks" placeholder="请选择框架" />
          <p class="text-sm text-muted-foreground">当前值：{{ grouped || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="clearable">
      <DemoBlock
        title="可清除"
        description="设置 clearable 显示清除按钮"
        code='<ESelect v-model="value" :options="options" clearable placeholder="可清除选择" />'
      >
        <div class="max-w-sm">
          <ESelect v-model="clearable" :options="fruits" :clearable="true" placeholder="可清除选择" />
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁用选择器"
        code='<ESelect v-model="value" :options="options" :disabled="true" />'
      >
        <div class="max-w-sm">
          <ESelect v-model="disabled" :options="frameworks" :disabled="true" />
        </div>
      </DemoBlock>
    </section>

    <section id="sizes">
      <DemoBlock
        title="尺寸变体"
        description="支持 sm / default / lg 三种尺寸"
        code='<ESelect size="sm" :options="options" placeholder="小尺寸" />
<ESelect :options="options" placeholder="默认尺寸" />
<ESelect size="lg" :options="options" placeholder="大尺寸" />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="sizeSm" size="sm" :options="fruits" placeholder="小尺寸 sm" />
          <ESelect :options="fruits" placeholder="默认尺寸 default" />
          <ESelect v-model="sizeLg" size="lg" :options="fruits" placeholder="大尺寸 lg" />
        </div>
      </DemoBlock>
    </section>

    <section id="filterable">
      <DemoBlock
        title="可搜索选择器"
        description="设置 filterable 启用搜索过滤"
        code='<ESelect v-model="searchValue" :options="options" filterable placeholder="输入搜索..." />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="searchValue" :options="fruits" filterable placeholder="输入搜索..." />
          <p class="text-sm text-muted-foreground">当前值：{{ searchValue || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="multiple">
      <DemoBlock
        title="多选模式"
        description="设置 multiple 启用多选"
        code='<ESelect v-model="multiValue" :options="options" multiple placeholder="选择多个" />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="multiValue" :options="fruits" multiple placeholder="选择多个" />
          <p class="text-sm text-muted-foreground">已选：{{ multiValue.length > 0 ? multiValue.join(', ') : '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="collapse-tags">
      <DemoBlock
        title="多选标签折叠"
        description="设置 collapse-tags 折叠多选标签，节省空间"
        code='<ESelect v-model="collapseValue" :options="options" multiple collapse-tags />'
      >
        <div class="space-y-3 max-w-sm">
          <ESelect v-model="collapseValue" :options="fruits" multiple collapse-tags placeholder="选择多个（标签折叠）" />
          <p class="text-sm text-muted-foreground">已选：{{ collapseValue.length > 0 ? collapseValue.join(', ') : '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
