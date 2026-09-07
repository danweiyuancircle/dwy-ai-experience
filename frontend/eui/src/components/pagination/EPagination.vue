<!--
  EPagination 分页组件
  基于 reka-ui Pagination 封装，类 Element Plus API
  页码默认露出首尾数字并用省略号折叠；只保留上一页/下一页，不含首页/末页双箭头
  每页条数选项由调用方传 pageSizes，对齐各自后端上限，组件不绑定业务限额
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
} from 'lucide-vue-next'
import {
  PaginationRoot,
  PaginationList,
  PaginationListItem,
  PaginationPrev,
  PaginationNext,
  PaginationEllipsis,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { buttonVariants } from '@/components/button/types'
import { useEuiMobile } from '@/composables/useEuiMobile'
import type { EPaginationProps, EPaginationEmits } from './types'

const props = withDefaults(defineProps<EPaginationProps>(), {
  modelValue: 1,
  total: 0,
  pageSize: 10,
  siblingCount: 1,
  showSizeChanger: false,
  pageSizes: () => [10, 20, 50, 100],
  showTotal: false,
  jumper: false,
  layout: 'total, sizes, prev, pager, next, jumper',
  disabled: false,
  mode: 'auto',
})

/** 窄屏时 auto 切简版，避免页码+条数选择把行撑爆 */
const isMobile = useEuiMobile()
const isSimpleMode = computed(() => {
  if (props.mode === 'simple') return true
  if (props.mode === 'full') return false
  return isMobile.value
})

const emit = defineEmits<EPaginationEmits>()

const pageCount = computed(() => {
  if (!props.total || !props.pageSize) return 1
  return Math.ceil(props.total / props.pageSize)
})

const layoutItems = computed(() =>
  props.layout.split(',').map(s => s.trim()).filter(Boolean),
)

const jumperValue = ref('')

function onPageChange(page: number) {
  emit('update:modelValue', page)
  emit('change', page)
}

function onSizeChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const size = Number(target.value)
  emit('update:pageSize', size)
  emit('size-change', size)
  // 每页条数改变时强制跳回第 1 页，避免超出新的页数范围
  emit('update:modelValue', 1)
  emit('change', 1)
}

function onJumperSubmit() {
  const page = Number(jumperValue.value)
  if (!page || Number.isNaN(page)) {
    jumperValue.value = ''
    return
  }
  const clamped = Math.max(1, Math.min(page, pageCount.value))
  onPageChange(clamped)
  jumperValue.value = ''
}

function hasLayout(item: string): boolean {
  return layoutItems.value.includes(item)
}
</script>

<template>
  <div
    data-slot="pagination-wrapper"
    :class="cn(
      'flex items-center gap-4 flex-wrap',
      disabled && 'opacity-50 pointer-events-none',
      props.class,
    )"
  >
    <template v-for="layoutItem in layoutItems" :key="layoutItem">
      <!-- Total text -->
      <span
        v-if="layoutItem === 'total' && showTotal && total !== undefined && !isSimpleMode"
        data-slot="pagination-total"
        class="text-sm text-muted-foreground shrink-0"
      >
        共 {{ total }} 条
      </span>

      <!-- Page size selector -->
      <select
        v-if="layoutItem === 'sizes' && showSizeChanger && !isSimpleMode"
        data-slot="pagination-size-changer"
        :value="pageSize"
        :disabled="disabled"
        class="h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:border-ring shrink-0"
        @change="onSizeChange"
      >
        <option
          v-for="size in pageSizes"
          :key="size"
          :value="size"
        >
          {{ size }} 条/页
        </option>
      </select>

      <!-- Pager group: prev, pager, next are rendered together inside PaginationRoot -->
      <PaginationRoot
        v-if="layoutItem === 'pager'"
        data-slot="pagination"
        :page="modelValue"
        :total="total"
        :items-per-page="pageSize"
        :sibling-count="siblingCount"
        show-edges
        :disabled="disabled"
        :class="cn('flex justify-center')"
        @update:page="onPageChange"
      >
        <PaginationList
          v-slot="{ items: paginationItems }"
          data-slot="pagination-content"
          :class="cn('flex flex-row items-center gap-1')"
        >
          <!-- Previous page button -->
          <PaginationPrev
            v-if="hasLayout('prev')"
            data-slot="pagination-previous"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronLeft class="size-4" />
          </PaginationPrev>

          <!-- 简版：当前页 / 总页，不铺页码 -->
          <span
            v-if="isSimpleMode"
            data-slot="pagination-simple"
            class="px-2 text-sm tabular-nums text-muted-foreground"
          >
            {{ modelValue }} / {{ pageCount }}
          </span>

          <!-- Page number items -->
          <template v-for="(paginationItem, index) in paginationItems" :key="index">
            <template v-if="!isSimpleMode">
            <PaginationListItem
              v-if="paginationItem.type === 'page'"
              data-slot="pagination-item"
              :value="paginationItem.value"
              :class="cn(
                buttonVariants({
                  variant: paginationItem.value === modelValue ? 'outline' : 'ghost',
                  size: 'icon',
                }),
                'size-9',
              )"
            >
              {{ paginationItem.value }}
            </PaginationListItem>

            <PaginationEllipsis
              v-else
              data-slot="pagination-ellipsis"
              :index="index"
              :class="cn('flex size-9 items-center justify-center')"
            >
              <MoreHorizontal class="size-4" />
              <span class="sr-only">More pages</span>
            </PaginationEllipsis>
            </template>
          </template>

          <!-- Next page button -->
          <PaginationNext
            v-if="hasLayout('next')"
            data-slot="pagination-next"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronRight class="size-4" />
          </PaginationNext>
        </PaginationList>
      </PaginationRoot>

      <!-- Jumper -->
      <div
        v-if="layoutItem === 'jumper' && jumper && !isSimpleMode"
        data-slot="pagination-jumper"
        class="flex items-center gap-2 text-sm text-muted-foreground shrink-0"
      >
        <span>前往</span>
        <input
          v-model="jumperValue"
          type="number"
          :disabled="disabled"
          :min="1"
          :max="pageCount"
          class="h-9 w-14 rounded-md border border-input bg-transparent px-2 py-1 text-center text-sm shadow-xs focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:border-ring [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          @keydown.enter="onJumperSubmit"
          @blur="onJumperSubmit"
        />
        <span>页</span>
      </div>
    </template>
  </div>
</template>
