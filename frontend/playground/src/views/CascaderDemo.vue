<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref<(string | number)[]>([])
const filterValue = ref<(string | number)[]>([])
const multiValue = ref<(string | number)[][]>([])

const options = [
  {
    label: '浙江省',
    value: 'zhejiang',
    children: [
      {
        label: '杭州市',
        value: 'hangzhou',
        children: [
          { label: '西湖区', value: 'xihu' },
          { label: '余杭区', value: 'yuhang' },
        ],
      },
      {
        label: '宁波市',
        value: 'ningbo',
        children: [
          { label: '海曙区', value: 'haishu' },
          { label: '江北区', value: 'jiangbei' },
        ],
      },
    ],
  },
  {
    label: '江苏省',
    value: 'jiangsu',
    children: [
      {
        label: '南京市',
        value: 'nanjing',
        children: [
          { label: '玄武区', value: 'xuanwu' },
          { label: '鼓楼区', value: 'gulou' },
        ],
      },
      {
        label: '苏州市',
        value: 'suzhou',
        children: [
          { label: '姑苏区', value: 'gusu' },
          { label: '工业园区', value: 'gongyeyuan' },
        ],
      },
    ],
  },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'filterable', label: '可搜索' },
  { id: 'multiple', label: '多选' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: '(string | number)[] | (string | number)[][]', default: '—', description: '绑定值，单选为路径数组，多选为路径数组的数组' },
  { name: 'options', type: 'CascaderOption[]', default: '[]', description: '级联选项数据' },
  { name: 'placeholder', type: 'string', default: '—', description: '占位文本' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'clearable', type: 'boolean', default: 'false', description: '是否可清空' },
  { name: 'filterable', type: 'boolean', default: 'false', description: '是否可搜索' },
  { name: 'lazy', type: 'boolean', default: 'false', description: '是否懒加载子节点' },
  { name: 'loadFn', type: '(option: CascaderOption) => Promise<CascaderOption[]>', default: '—', description: '懒加载时加载子节点的函数' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否多选' },
  { name: 'collapseTags', type: 'boolean', default: 'false', description: '多选时是否折叠标签为 "+N"' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: (string | number)[] | (string | number)[][])', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(value: (string | number)[] | (string | number)[][])', description: '选中值改变时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Cascader 级联选择器"
    description="用于从层级数据中逐级选择，支持搜索、多选、懒加载。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于省市区选择、组织架构选择、分类目录等具有层级关系的数据选择场景。支持搜索过滤和多选模式。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 options 传入层级数据，v-model 绑定选中的路径"
        code='<ECascader v-model="value" :options="options" placeholder="请选择地区" clearable />'
      >
        <div class="space-y-2 max-w-sm">
          <ECascader v-model="basicValue" :options="options" placeholder="请选择地区" clearable />
          <p class="text-sm text-muted-foreground">选中路径：{{ basicValue.length ? basicValue.join(' / ') : '（未选择）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="filterable">
      <DemoBlock
        title="可搜索"
        description="开启 filterable 后可通过输入关键字搜索选项"
        code='<ECascader v-model="value" :options="options" filterable placeholder="输入关键字搜索" />'
      >
        <div class="max-w-sm">
          <ECascader v-model="filterValue" :options="options" filterable placeholder="输入关键字搜索" clearable />
        </div>
      </DemoBlock>
    </section>

    <section id="multiple">
      <DemoBlock
        title="多选"
        description="开启 multiple 允许选择多条路径，collapseTags 折叠多余标签"
        code='<ECascader v-model="value" :options="options" multiple collapseTags placeholder="多选地区" />'
      >
        <div class="space-y-2 max-w-sm">
          <ECascader v-model="multiValue" :options="options" multiple collapse-tags placeholder="多选地区" clearable />
          <p class="text-sm text-muted-foreground">已选 {{ multiValue.length }} 项</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止交互"
        code='<ECascader :options="options" disabled placeholder="禁用状态" />'
      >
        <div class="max-w-sm">
          <ECascader :options="options" disabled placeholder="禁用状态" />
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
