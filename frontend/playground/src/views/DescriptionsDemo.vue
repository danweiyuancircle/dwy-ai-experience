<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'

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
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Descriptions 描述列表</h1>
    <p class="text-muted-foreground mb-6">描述信息展示组件，支持多列布局、合并单元格和边框样式。</p>

    <DemoBlock
      title="基础描述列表"
      description="默认 3 列布局展示键值对信息"
      code='<EDescriptions title="用户信息" :items="items" />'
    >
      <EDescriptions title="用户信息" :items="userItems" />
    </DemoBlock>

    <DemoBlock
      title="带边框样式"
      description="设置 bordered 显示完整边框"
      code='<EDescriptions :items="items" :bordered="true" />'
    >
      <EDescriptions title="用户详情" :items="userItems" :bordered="true" />
    </DemoBlock>

    <DemoBlock
      title="自定义列数"
      description="通过 columns 设置每行显示的列数"
      code='<EDescriptions :items="items" :columns="2" />'
    >
      <EDescriptions :items="userItems" :columns="2" title="两列布局" />
    </DemoBlock>

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
  </div>
</template>
