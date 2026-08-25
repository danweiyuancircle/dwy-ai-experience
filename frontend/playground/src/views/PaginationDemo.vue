<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const page1 = ref(1)
const page2 = ref(3)
const page3 = ref(1)
const pageSize3 = ref(20)
const page4 = ref(1)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础分页' },
  { id: 'total', label: '显示总数' },
  { id: 'size-changer', label: '可改变每页数量' },
  { id: 'jumper', label: '带跳转分页' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: 'number', default: '-', description: '当前页码，支持 v-model' },
  { name: 'total', type: 'number', default: '0', description: '数据总条数' },
  { name: 'pageSize', type: 'number', default: '10', description: '每页显示条数，支持 v-model:pageSize' },
  { name: 'siblingCount', type: 'number', default: '1', description: '当前页两侧显示的页码数量' },
  { name: 'showSizeChanger', type: 'boolean', default: 'false', description: '是否显示每页条数选择器' },
  { name: 'pageSizes', type: 'number[]', default: '[10, 20, 50, 100]', description: '每页条数选项，由调用方按后端上限传入' },
  { name: 'showTotal', type: 'boolean', default: 'false', description: '是否显示数据总条数' },
  { name: 'jumper', type: 'boolean', default: 'false', description: '是否显示页码跳转输入框' },
  { name: 'layout', type: 'string', default: '-', description: '布局配置，如 "total, prev, pager, next, jumper"' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用分页控件' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(page: number)', description: '当前页码变更时触发' },
  { name: 'change', params: '(page: number)', description: '翻页时触发' },
  { name: 'update:pageSize', params: '(size: number)', description: '每页条数变更时触发' },
  { name: 'size-change', params: '(size: number)', description: '每页条数变更时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Pagination 分页"
    description="数据分页组件，支持总数显示、页码大小切换、当前页控制。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于数据列表、表格等需要分页展示大量数据的场景。支持显示总条数、切换每页条数、快速跳转到指定页码等功能，帮助用户高效浏览和定位数据。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础分页"
        description="页码带省略号和末页数字，只保留上一页 / 下一页"
        code='<EPagination v-model="page" :total="100" />'
      >
        <EPagination v-model="page1" :total="100" />
      </DemoBlock>
    </section>

    <section id="total">
      <DemoBlock
        title="显示总数"
        description="设置 showTotal 显示数据总条数"
        code='<EPagination v-model="page" :total="250" :pageSize="10" showTotal />'
      >
        <EPagination v-model="page2" :total="250" :pageSize="10" :showTotal="true" />
      </DemoBlock>
    </section>

    <section id="size-changer">
      <DemoBlock
        title="可改变每页数量"
        description="showSizeChanger 打开后，pageSizes 由调用方按后端上限传入"
        code='<EPagination
  v-model="page"
  :total="500"
  v-model:pageSize="pageSize"
  :pageSizes="[10, 20, 50, 100]"
  showSizeChanger
  showTotal
/>'
      >
        <EPagination
          v-model="page3"
          :total="500"
          v-model:pageSize="pageSize3"
          :showSizeChanger="true"
          :showTotal="true"
          :pageSizes="[10, 20, 50, 100]"
        />
      </DemoBlock>
    </section>

    <section id="jumper">
      <DemoBlock
        title="带跳转分页"
        description="设置 jumper 和 layout 启用页码跳转输入框"
        code='<EPagination v-model="page" :total="500" jumper layout="total, prev, pager, next, jumper" />'
      >
        <EPagination
          v-model="page4"
          :total="500"
          jumper
          layout="total, prev, pager, next, jumper"
          :showTotal="true"
        />
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
