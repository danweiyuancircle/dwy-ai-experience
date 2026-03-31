<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const count = ref(1234567)
const timer = ref<ReturnType<typeof setInterval> | null>(null)

function startCounter() {
  if (timer.value) return
  count.value = 0
  timer.value = setInterval(() => {
    count.value += 12345
    if (count.value >= 1234567) {
      count.value = 1234567
      clearInterval(timer.value!)
      timer.value = null
    }
  }, 100)
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础统计数字' },
  { id: 'prefix-suffix', label: '前缀和后缀' },
  { id: 'precision', label: '精度控制' },
  { id: 'dashboard', label: '仪表板卡片' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'title', type: 'string', default: '-', description: '统计项标题' },
  { name: 'value', type: 'number | string', default: '-', description: '统计数值' },
  { name: 'prefix', type: 'string', default: '-', description: '数值前缀（如货币符号 ¥）' },
  { name: 'suffix', type: 'string', default: '-', description: '数值后缀（如单位 %、ms）' },
  { name: 'precision', type: 'number', default: '-', description: '小数位精度' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'title', description: '自定义标题区域' },
  { name: 'prefix', description: '自定义前缀内容（可放图标等）' },
  { name: 'suffix', description: '自定义后缀内容' },
]
</script>

<template>
  <ComponentDoc
    title="Statistic 统计数值"
    description="数字统计展示组件，支持前缀、后缀、精度和自定义渲染。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于管理后台仪表板、数据概览页面中展示关键数字指标，如总用户数、营收金额、转化率、响应时间等。通过 prefix/suffix 添加单位符号，precision 控制小数精度。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础统计数字"
        description="展示关键数字指标"
        code='<EStatistic title="总用户数" :value="12345" />'
      >
        <div class="grid grid-cols-3 gap-6">
          <EStatistic title="总用户数" :value="12345" />
          <EStatistic title="本月订单" :value="567" />
          <EStatistic title="活跃会员" :value="8924" />
        </div>
      </DemoBlock>
    </section>

    <section id="prefix-suffix">
      <DemoBlock
        title="带前缀和后缀"
        description="通过 prefix 和 suffix 添加单位或符号"
        code='<EStatistic title="账户余额" :value="19999.99" prefix="¥" :precision="2" />
<EStatistic title="增长率" :value="12.5" suffix="%" />'
      >
        <div class="grid grid-cols-3 gap-6">
          <EStatistic title="账户余额" :value="19999.99" prefix="¥" :precision="2" />
          <EStatistic title="季度增长" :value="12.5" suffix="%" :precision="1" />
          <EStatistic title="服务时长" :value="99.9" suffix="%" />
        </div>
      </DemoBlock>
    </section>

    <section id="precision">
      <DemoBlock
        title="精度控制"
        description="通过 precision 设置小数位数"
        code='<EStatistic title="完成率" :value="87.654" :precision="2" suffix="%" />'
      >
        <div class="grid grid-cols-3 gap-6">
          <EStatistic title="整数" :value="100" />
          <EStatistic title="一位小数" :value="87.6" :precision="1" suffix="%" />
          <EStatistic title="两位小数" :value="3.14159" :precision="2" />
        </div>
      </DemoBlock>
    </section>

    <section id="dashboard">
      <DemoBlock
        title="仪表板统计卡片"
        description="常见的管理后台统计数字展示场景"
      >
        <div class="grid grid-cols-2 gap-4">
          <div class="border rounded-lg p-4 space-y-1">
            <EStatistic title="今日访问量" :value="28456" />
            <p class="text-xs text-green-600">+12.5% 较昨日</p>
          </div>
          <div class="border rounded-lg p-4 space-y-1">
            <EStatistic title="本月营收" :value="1289630" prefix="¥" />
            <p class="text-xs text-green-600">+8.3% 较上月</p>
          </div>
          <div class="border rounded-lg p-4 space-y-1">
            <EStatistic title="转化率" :value="4.67" :precision="2" suffix="%" />
            <p class="text-xs text-red-500">-0.5% 较上月</p>
          </div>
          <div class="border rounded-lg p-4 space-y-1">
            <EStatistic title="平均响应时间" :value="98" suffix="ms" />
            <p class="text-xs text-green-600">性能良好</p>
          </div>
        </div>
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
