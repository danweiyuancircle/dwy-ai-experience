<!--
  指标卡栅格。
  断点看这块内容区的宽度，不看浏览器窗口：侧栏会占掉一截视口。
-->
<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'MetricGrid' })

const props = withDefaults(
  defineProps<{
    /**
     * 内容区够宽时的列数。
     * 枚举 ``{2, 3, 5}``，默认 ``3``。
     * 更窄时先一列，36rem 起两列。
     */
    columns?: 2 | 3 | 5
  }>(),
  { columns: 3 },
)

/** 宽屏列数。基础一列写在模板上，这里只追加断点。 */
const columnClass = computed(() => {
  if (props.columns === 2) return '@min-[36rem]:grid-cols-2'
  if (props.columns === 5) {
    return '@min-[36rem]:grid-cols-2 @min-[56rem]:grid-cols-3 @min-[72rem]:grid-cols-5'
  }
  return '@min-[36rem]:grid-cols-2 @min-[56rem]:grid-cols-3'
})
</script>

<template>
  <!-- @container 包在外面：栅格自己不能拿自己的宽度当容器。 -->
  <div class="@container min-w-0">
    <div data-card-grid class="grid min-w-0 grid-cols-1 gap-4" :class="columnClass">
      <slot />
    </div>
  </div>
</template>
