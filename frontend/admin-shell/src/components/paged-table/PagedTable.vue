<!--
  数据列表壳：顶栏、表格滚动区、分页区三段。
  表格区 min-w-0：flex 子项默认按内容撑开，手机上表比屏幕宽时滑不动，字被卡片裁掉。
  搜索和筛选写在 #toolbar，靠右的新建写在 #actions。壳不解释这些按钮。
  total 不传时不渲染分页（全量小表）。total 为 0 时默认藏分页。
  没有行时不挂表格，列名和边框都不出现，只留页面的 #empty。
-->
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, useSlots, watch, type Slots } from 'vue'
import { EEmpty, EPagination, ESpinner, ETable, type TableColumn } from '@dwydev/eui'
import { DEFAULT_LIST_PAGE_SIZE, LIST_PAGE_SIZES } from './pageSizes'

defineOptions({ name: 'PagedTable' })

const props = withDefaults(
  defineProps<{
    /** 列定义，原样交给 ETable */
    columns?: TableColumn[]
    /**
     * 当前页行。壳不读取字段。
     * 用 any：各页行接口不同，收窄后页面回调无法再传进来。
     */
    data?: readonly any[]
    /** 表格加载蒙层 */
    loading?: boolean
    /** 行唯一字段，默认 id，与 ETable 一致 */
    rowKey?: string
    /**
     * 行 class。参数用 any，原因同 data。
     * 静态字符串或按行计算。
     */
    rowClassName?: string | ((row: any, index: number) => string)
    /** 加在 ETable 上的 class，例如 table-fixed */
    tableClass?: string
    /** 行展开。用量明细在用 */
    expandable?: boolean
    /** 当前展开的行 key */
    expandedRowKeys?: (string | number)[]
    /** 当前页，从 1。未分页时可不传 */
    page?: number
    /** 每页条数。未分页时可不传 */
    pageSize?: number
    /**
     * 总条数。不传表示这张表没有分页。
     * 传 0 且 hideWhenEmpty 时不渲染分页条。
     */
    total?: number
    /** 每页条数选项。默认 20 / 50 / 100 */
    pageSizes?: number[]
    /** total 为 0 时是否隐藏分页。默认隐藏 */
    hideWhenEmpty?: boolean
    /** 分页条是否显示总条数。公告页自己写了「共 N 条」，关掉避免重复 */
    showTotal?: boolean
    /**
     * 表格区是否吃掉父级剩余高度并内部滚动。
     * 整页列表开；卡片里的表关掉，避免把卡片撑成一屏。
     */
    fill?: boolean
  }>(),
  {
    columns: () => [],
    data: () => [],
    loading: false,
    rowKey: 'id',
    pageSize: DEFAULT_LIST_PAGE_SIZE,
    expandable: false,
    pageSizes: () => [...LIST_PAGE_SIZES],
    hideWhenEmpty: true,
    showTotal: true,
    fill: true,
  },
)

const emit = defineEmits<{
  /** 翻页。页码从 1 */
  'update:page': [page: number]
  /** 改每页条数。回到第 1 页由页面自己的加载函数做 */
  'update:pageSize': [size: number]
  /** 表头排序。direction 为 null 表示取消 */
  sort: [key: string, direction: 'asc' | 'desc' | null]
  /** 点击行 */
  'row-click': [row: any, index: number]
  /** 展开行变化 */
  'update:expandedRowKeys': [keys: (string | number)[]]
}>()

// 显式约束插槽集合，保证独立构建 d.ts 时不产生循环推断。
const slots: Slots = useSlots()
const tableBody = ref<HTMLElement>()
const hasHorizontalOverflow = ref(false)
const scrollHintId = `table-scroll-hint-${useId()}`
let resizeObserver: ResizeObserver | undefined

function measureOverflow() {
  const scroller = tableBody.value?.querySelector<HTMLElement>('[data-slot="table-container"]')
  hasHorizontalOverflow.value = !!scroller && scroller.scrollWidth > scroller.clientWidth + 1
}

async function observeTable() {
  await nextTick()
  resizeObserver?.disconnect()
  const scroller = tableBody.value?.querySelector<HTMLElement>('[data-slot="table-container"]')
  if (scroller && resizeObserver) {
    resizeObserver.observe(scroller)
    const table = scroller.querySelector('table')
    if (table) resizeObserver.observe(table)
  }
  measureOverflow()
}

watch([() => props.data, () => props.columns], observeTable, { flush: 'post' })
onMounted(() => {
  if (typeof ResizeObserver !== 'undefined') resizeObserver = new ResizeObserver(measureOverflow)
  void observeTable()
  window.addEventListener('resize', measureOverflow)
})
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('resize', measureOverflow)
})

/** 壳自己摆的槽。其余 #cell-* / #expand 才进表格，避免新建按钮漏进表头。 */
const SHELL_SLOT_NAMES = new Set(['toolbar', 'actions', 'empty'])

const forwardedSlotNames = computed<string[]>(() =>
  Object.keys(slots).filter((name) => !SHELL_SLOT_NAMES.has(name)),
)

/**
 * 没有行。加载中同样不画列名，避免先闪出表头再变成空。
 */
const isEmpty = computed(() => props.data.length === 0)

/**
 * ETable 把行收成可变 Record。各页行类型更窄，壳不改字段，只在这一处放宽。
 */
const tableData = computed(() => props.data as Record<string, any>[])

/** 有 total 才是分页表；空结果默认不画分页条 */
const showPagination = computed(() => {
  if (props.total === undefined) return false
  if (props.hideWhenEmpty && props.total <= 0) return false
  return true
})

/**
 * 把 ETable 的排序原样抛给页面。
 * @param key 列 key
 * @param direction 升降序；null 为取消
 */
function handleSort(key: string, direction: 'asc' | 'desc' | null) {
  emit('sort', key, direction)
}

/**
 * 把行点击原样抛给页面。
 * @param row 当前行
 * @param index 行下标，从 0
 */
function handleRowClick(row: any, index: number) {
  emit('row-click', row, index)
}

/**
 * 把展开行 key 原样抛给页面。
 * @param keys 当前展开的行 key
 */
function handleExpanded(keys: (string | number)[]) {
  emit('update:expandedRowKeys', keys)
}
</script>

<template>
  <div class="flex min-h-0 w-full min-w-0 max-w-full flex-col gap-3">
    <!-- #actions 用 ml-auto 靠右。只有按钮、没有筛选时也靠右。 -->
    <div v-if="slots.toolbar || slots.actions" class="flex flex-wrap items-center gap-2">
      <slot name="toolbar" />
      <div v-if="slots.actions" class="ml-auto flex flex-wrap items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    <p
      v-if="hasHorizontalOverflow"
      :id="scrollHintId"
      data-slot="table-scroll-hint"
      class="text-xs text-muted-foreground"
    >
      左右滑动查看全部列与操作；键盘可聚焦表格后使用方向键。
    </p>
    <!-- 没有行时不挂表格。文案用页面 #empty；没写则一句暂无数据。 -->
    <div
      v-if="isEmpty"
      class="paged-table-empty flex items-center justify-center"
      :class="fill ? 'min-h-0 flex-1' : 'py-10'"
    >
      <ESpinner v-if="loading" size="lg" />
      <slot v-else name="empty">
        <EEmpty title="暂无数据" />
      </slot>
    </div>
    <div
      v-else
      ref="tableBody"
      class="paged-table-body min-h-0 min-w-0 max-w-full overflow-auto rounded-md border"
      :class="fill ? 'flex-1' : undefined"
    >
      <ETable
        :tabindex="hasHorizontalOverflow ? 0 : undefined"
        :role="hasHorizontalOverflow ? 'region' : undefined"
        :aria-label="hasHorizontalOverflow ? '数据表格，可横向滚动' : undefined"
        :aria-describedby="hasHorizontalOverflow ? scrollHintId : undefined"
        :class="tableClass"
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :row-key="rowKey"
        :row-class-name="rowClassName"
        :expandable="expandable"
        :expanded-row-keys="expandedRowKeys"
        @sort="handleSort"
        @row-click="handleRowClick"
        @update:expanded-row-keys="handleExpanded"
      >
        <template v-for="slotName in forwardedSlotNames" :key="slotName" #[slotName]="slotProps">
          <slot :name="slotName" v-bind="slotProps ?? {}" />
        </template>
      </ETable>
    </div>
    <EPagination
      v-if="showPagination"
      :model-value="page"
      :total="total"
      :page-size="pageSize"
      :page-sizes="pageSizes"
      :show-total="showTotal"
      show-size-changer
      @update:model-value="emit('update:page', $event)"
      @update:page-size="emit('update:pageSize', $event)"
    />
  </div>
</template>
