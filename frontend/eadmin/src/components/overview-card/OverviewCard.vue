<!--
  概览卡外壳。指标卡和入口卡共用，避免两套圆角、内边距和图标位置。
  图标井固定在右侧。有 to 时箭头排在井左边，悬停只改边框和箭头颜色。
  没有 to 时不放箭头，也不加悬停，静止时不会假装能点。
-->
<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { ArrowUpRight } from 'lucide-vue-next'
import { ECard } from '@dwydev/eui'

defineOptions({ name: 'OverviewCard' })

defineProps<{
  /** 点击跳转的路径。不传则整卡只展示。示例：`'/factors'`。 */
  to?: string
}>()
</script>

<template>
  <component
    :is="to ? RouterLink : 'div'"
    v-bind="to ? { to } : {}"
    class="block h-full"
    :class="to ? 'group' : undefined"
  >
    <ECard class="h-full" :class="to ? 'transition-colors group-hover:border-primary/40' : undefined">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <slot />
        </div>
        <div v-if="to || $slots.icon" class="flex shrink-0 items-center gap-2">
          <ArrowUpRight
            v-if="to"
            class="size-4 text-muted-foreground/40 transition-colors group-hover:text-primary"
          />
          <div
            v-if="$slots.icon"
            class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary"
          >
            <slot name="icon" />
          </div>
        </div>
      </div>
    </ECard>
  </component>
</template>
