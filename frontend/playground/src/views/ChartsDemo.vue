<script setup lang="ts">
import { computed, ref } from 'vue'
import { EButton, ECard } from '@dwydev/eui'
import { EBarChart, EDonutChart, ELineChart } from '@dwydev/eui/charts'
import type { EChartSeries } from '@dwydev/eui/charts'

const secondWeek = ref(false)
const days = computed(() => secondWeek.value
  ? ['11/13', '11/14', '11/15', '11/16', '11/17', '11/18', '11/19']
  : ['11/20', '11/21', '11/22', '11/23', '11/24', '11/25', '11/26'])
const visits = computed<EChartSeries[]>(() => [
  { key: 'web', label: '站点访问', values: secondWeek.value ? [76, 92, 86, 110, 99, 116, 130] : [104, 123, null, 158, 147, 184, 176] },
  { key: 'app', label: '应用访问', values: secondWeek.value ? [44, 55, 51, 63, 61, 65, 76] : [57, 69, 65, 91, 83, 106, 113] },
])
const counts = [{ key: 'closed', label: '已处理', values: [82, 63, 44, 31] }]
const sources = [
  { key: 'direct', label: '直接访问', value: 645 },
  { key: 'internal', label: '站内推荐', value: 409 },
  { key: 'external', label: '外部链接', value: 186 },
]
</script>

<template>
  <div class="max-w-5xl space-y-5">
    <header>
      <h1 class="text-2xl font-bold">图表</h1>
      <p class="text-muted-foreground mt-2 text-sm">用 EUI 图表呈现趋势、类别对比和占比。展开图下方的数据可查看具体数值。</p>
    </header>
    <div class="grid gap-4 lg:grid-cols-2">
      <ECard title="访问趋势">
        <template #action>
          <EButton size="sm" variant="outline" @click="secondWeek = !secondWeek">切换周次</EButton>
        </template>
        <ELineChart label="访问趋势" :categories="days" :series="visits" />
      </ECard>
      <ECard title="访问来源">
        <EDonutChart label="访问来源" :items="sources" />
      </ECard>
      <ECard title="各模块处理量">
        <EBarChart label="各模块处理量" :categories="['内容', '运营', '审核', '工单']" :series="counts" />
      </ECard>
    </div>
    <p class="text-muted-foreground text-sm">
      从 <code>@dwydev/eui/charts</code> 导入。需要组合图、缩放与其他高级配置时，可直接使用
      <a class="underline" href="https://unovis.dev/docs/">Unovis</a>。
    </p>
  </div>
</template>
