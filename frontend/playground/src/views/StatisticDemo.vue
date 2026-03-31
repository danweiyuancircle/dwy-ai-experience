<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Statistic 统计数值</h1>
    <p class="text-muted-foreground mb-6">数字统计展示组件，支持前缀、后缀、精度和自定义渲染。</p>

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
  </div>
</template>
