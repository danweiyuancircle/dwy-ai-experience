<!--
  固定的数据概览页。
  顺序是：无标题指标、分组指标、快捷入口、默认插槽、页底说明。
  哪一段没数据就空过。页面只注入数据和插槽，不自己排栅格。
-->
<script setup lang="ts">
import ActionLinkCard from '../action-link-card/ActionLinkCard.vue'
import MetricGrid from '../metric-grid/MetricGrid.vue'
import MetricSection from '../metric-section/MetricSection.vue'
import StatCard from '../stat-card/StatCard.vue'
import type { OverviewLink, OverviewMetric, OverviewSection } from './types'

defineOptions({ name: 'DataOverview' })

withDefaults(
  defineProps<{
    /** 没有分组标题的指标行。控制台首页用。默认空。 */
    metrics?: OverviewMetric[]
    /**
     * 无标题指标行的列数。
     * 枚举 ``{2, 3, 5}``，默认 ``3``。
     */
    metricColumns?: 2 | 3 | 5
    /** 带标题的分组。管理概览用。默认空。 */
    sections?: OverviewSection[]
    /** 快捷入口，排在分组下面。默认空。 */
    links?: OverviewLink[]
    /** 页底口径说明。空字符串不渲染。 */
    note?: string
  }>(),
  {
    metrics: () => [],
    metricColumns: 3,
    sections: () => [],
    links: () => [],
    note: '',
  },
)
</script>

<template>
  <div class="flex flex-col gap-6">
    <MetricGrid v-if="metrics.length > 0" :columns="metricColumns">
      <StatCard
        v-for="metric in metrics"
        :key="metric.title"
        :title="metric.title"
        :value="metric.value"
        :to="metric.to"
      >
        <template v-if="metric.icon" #icon>
          <component :is="metric.icon" class="size-5" />
        </template>
      </StatCard>
    </MetricGrid>

    <MetricSection v-for="section in sections" :key="section.title" :title="section.title">
      <MetricGrid :columns="section.columns ?? 3">
        <StatCard
          v-for="metric in section.metrics"
          :key="metric.title"
          :title="metric.title"
          :value="metric.value"
          :to="metric.to"
        >
          <template v-if="metric.icon" #icon>
            <component :is="metric.icon" class="size-5" />
          </template>
        </StatCard>
      </MetricGrid>
    </MetricSection>

    <MetricGrid v-if="links.length > 0" :columns="3">
      <ActionLinkCard
        v-for="link in links"
        :key="link.title"
        :title="link.title"
        :description="link.description"
        :to="link.to"
      >
        <template v-if="link.icon" #icon>
          <component :is="link.icon" class="size-5" />
        </template>
      </ActionLinkCard>
    </MetricGrid>

    <slot />

    <p v-if="note" class="text-xs text-muted-foreground">{{ note }}</p>
  </div>
</template>
