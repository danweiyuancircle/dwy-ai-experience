<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const userItems = [
  { label: '姓名', value: '张三' },
  { label: '邮箱', value: 'zhangsan@example.com' },
  { label: '手机', value: '138****5678' },
  { label: '角色', value: '系统管理员' },
  { label: '部门', value: '技术部' },
  { label: '注册时间', value: '2023-06-15 10:30:00' },
]

const orderItems = [
  { label: '订单号', value: 'ORD-20240115-001' },
  { label: '商品名称', value: 'EUI 企业许可证', span: 2 },
  { label: '单价', value: '¥1,999.00' },
  { label: '数量', value: '1' },
  { label: '总计', value: '¥1,999.00' },
  { label: '支付方式', value: '支付宝' },
  { label: '订单状态', value: '已完成' },
  { label: '备注', value: '请开具增值税专用发票', span: 3 },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础描述列表' },
  { id: 'bordered', label: '带边框样式' },
  { id: 'columns', label: '自定义列数' },
  { id: 'span', label: '跨列' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'items', type: 'DescriptionItem[]', default: '[]', description: '描述项数组，每项包含 label、value、span' },
  { name: 'columns', type: 'number', default: '3', description: '每行显示的列数' },
  { name: 'bordered', type: 'boolean', default: 'false', description: '是否显示完整边框' },
  { name: 'title', type: 'string', default: '-', description: '标题文字' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '自定义描述列表内容' },
  { name: 'title', description: '自定义标题区域' },
]
</script>

<template>
  <ComponentDoc
    title="Descriptions 描述列表"
    description="描述信息展示组件，支持多列布局、合并单元格和边框样式。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于详情页面中以键值对形式展示信息，如用户详情、订单信息、系统配置等。通过 columns 控制每行列数，span 实现跨列展示长文本内容。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础描述列表"
        description="默认 3 列布局展示键值对信息"
        code='<EDescriptions title="用户信息" :items="items" />'
      >
        <EDescriptions title="用户信息" :items="userItems" />
      </DemoBlock>
    </section>

    <section id="bordered">
      <DemoBlock
        title="带边框样式"
        description="设置 bordered 显示完整边框"
        code='<EDescriptions :items="items" :bordered="true" />'
      >
        <EDescriptions title="用户详情" :items="userItems" :bordered="true" />
      </DemoBlock>
    </section>

    <section id="columns">
      <DemoBlock
        title="自定义列数"
        description="通过 columns 设置每行显示的列数"
        code='<EDescriptions :items="items" :columns="2" />'
      >
        <EDescriptions :items="userItems" :columns="2" title="两列布局" />
      </DemoBlock>
    </section>

    <section id="span">
      <DemoBlock
        title="跨列（span）"
        description="单个 item 可通过 span 跨越多列"
        code='const items = [
  { label: "商品名称", value: "EUI 许可证", span: 2 },
  { label: "备注", value: "开票备注", span: 3 },
]'
      >
        <EDescriptions title="订单详情" :items="orderItems" :bordered="true" :columns="3" />
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
