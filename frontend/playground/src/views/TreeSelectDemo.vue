<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const singleValue = ref<string | number>()
const multipleValue = ref<(string | number)[]>([])
const checkableValue = ref<(string | number)[]>([])

const orgData = [
  {
    key: 'company',
    label: '总公司',
    children: [
      {
        key: 'tech',
        label: '技术部',
        children: [
          { key: 'frontend', label: '前端组' },
          { key: 'backend', label: '后端组' },
          { key: 'devops', label: '运维组' },
        ],
      },
      {
        key: 'product',
        label: '产品部',
        children: [
          { key: 'design', label: '设计组' },
          { key: 'pm', label: '产品经理组' },
        ],
      },
      {
        key: 'hr',
        label: '人力资源部',
        children: [
          { key: 'recruit', label: '招聘组' },
          { key: 'training', label: '培训组' },
        ],
      },
    ],
  },
]

const cityData = [
  {
    key: 'east',
    label: '华东地区',
    children: [
      { key: 'shanghai', label: '上海' },
      { key: 'hangzhou', label: '杭州' },
      { key: 'nanjing', label: '南京' },
    ],
  },
  {
    key: 'south',
    label: '华南地区',
    children: [
      { key: 'shenzhen', label: '深圳' },
      { key: 'guangzhou', label: '广州' },
    ],
  },
  {
    key: 'north',
    label: '华北地区',
    children: [
      { key: 'beijing', label: '北京' },
      { key: 'tianjin', label: '天津' },
    ],
  },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'multiple', label: '多选模式' },
  { id: 'checkable', label: '复选框模式' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: "string | number | (string | number)[]", description: '选中的值，支持 v-model' },
  { name: 'data', type: 'TreeNode[]', description: '树形结构数据' },
  { name: 'placeholder', type: 'string', default: "'Select...'", description: '占位提示文字' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否允许多选' },
  { name: 'checkable', type: 'boolean', default: 'false', description: '是否显示复选框' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发' },
  { name: 'change', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发' },
]

const slotsData = [
  { name: 'default', description: '默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="TreeSelect 树选择"
    description="将树形结构数据与下拉选择结合，适用于层级数据的选择场景，支持单选、多选和复选框模式。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于组织架构选择、地区层级选择、分类目录选择等需要从树形层级数据中选取节点的场景。相比普通 Select，TreeSelect 更适合具有父子关系的数据结构。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="单选模式，点击叶子节点直接选中并关闭下拉"
        code='<ETreeSelect v-model="value" :data="orgData" placeholder="请选择部门" />'
      >
        <div class="max-w-xs space-y-2">
          <ETreeSelect v-model="singleValue" :data="orgData" placeholder="请选择部门" />
          <p class="text-sm text-muted-foreground">当前值：{{ singleValue ?? '未选择' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="multiple">
      <DemoBlock
        title="多选模式"
        description="设置 multiple 后可以选择多个节点，选中值为数组"
        code='<ETreeSelect v-model="value" :data="cityData" multiple placeholder="请选择城市" />'
      >
        <div class="max-w-xs space-y-2">
          <ETreeSelect v-model="multipleValue" :data="cityData" multiple placeholder="请选择城市" />
          <p class="text-sm text-muted-foreground">当前值：{{ multipleValue.length ? multipleValue.join(', ') : '未选择' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="checkable">
      <DemoBlock
        title="复选框模式"
        description="设置 checkable 后每个节点带有复选框，方便批量勾选"
        code='<ETreeSelect v-model="value" :data="orgData" checkable placeholder="请勾选部门" />'
      >
        <div class="max-w-xs space-y-2">
          <ETreeSelect v-model="checkableValue" :data="orgData" checkable placeholder="请勾选部门" />
          <p class="text-sm text-muted-foreground">当前值：{{ checkableValue.length ? checkableValue.join(', ') : '未选择' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 后组件不可交互"
        code='<ETreeSelect :data="orgData" disabled placeholder="已禁用" />'
      >
        <div class="max-w-xs">
          <ETreeSelect :data="orgData" disabled placeholder="已禁用" />
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
