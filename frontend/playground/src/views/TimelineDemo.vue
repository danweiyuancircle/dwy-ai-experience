<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const reversed = ref(false)

const orderTimeline = [
  {
    title: '订单创建',
    content: '用户提交订单，系统自动分配订单号 ORD-20240115-001',
    timestamp: '2024-01-15 09:00:00',
    type: 'primary' as const,
  },
  {
    title: '支付成功',
    content: '用户通过支付宝完成付款，金额 ¥1,999.00',
    timestamp: '2024-01-15 09:05:23',
    type: 'success' as const,
  },
  {
    title: '商家接单',
    content: '商家确认订单，预计 2-3 个工作日内发货',
    timestamp: '2024-01-15 10:30:00',
    type: 'primary' as const,
  },
  {
    title: '已发货',
    content: '快递单号：SF123456789，已交由顺丰速运',
    timestamp: '2024-01-16 15:20:00',
    type: 'primary' as const,
  },
  {
    title: '配送中',
    content: '快件已到达目的地城市配送站',
    timestamp: '2024-01-17 08:00:00',
    type: 'warning' as const,
  },
]

const systemTimeline = [
  {
    title: '系统部署成功',
    content: 'v2.1.0 版本部署完成，所有服务正常运行',
    timestamp: '今天 14:30',
    type: 'success' as const,
  },
  {
    title: '数据库备份',
    content: '全量备份完成，备份文件大小 2.3 GB',
    timestamp: '今天 03:00',
    type: 'primary' as const,
  },
  {
    title: '异常告警',
    content: 'API 响应超时，已自动重启服务',
    timestamp: '昨天 23:45',
    type: 'danger' as const,
  },
  {
    title: '用户反馈',
    content: '收到 3 条新的用户反馈，待处理',
    timestamp: '昨天 18:00',
    type: 'warning' as const,
  },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Timeline 时间线</h1>
    <p class="text-muted-foreground mb-6">时间轴组件，用于展示有时间顺序的事件序列。</p>

    <DemoBlock
      title="订单状态时间线"
      description="不同类型（primary/success/warning/danger）对应不同颜色节点"
      code='<ETimeline :items="timeline" />'
    >
      <ETimeline :items="orderTimeline" />
    </DemoBlock>

    <DemoBlock
      title="反向时间线"
      description="设置 reverse 倒序显示（最新在上）"
      code='<ETimeline :items="timeline" :reverse="true" />'
    >
      <div class="space-y-3">
        <ESwitch v-model="reversed" label="倒序显示（最新在上）" />
        <ETimeline :items="systemTimeline" :reverse="reversed" />
      </div>
    </DemoBlock>
  </div>
</template>
