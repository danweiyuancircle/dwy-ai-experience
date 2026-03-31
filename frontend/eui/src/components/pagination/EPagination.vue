<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  MoreHorizontal,
} from 'lucide-vue-next'
import {
  PaginationRoot,
  PaginationList,
  PaginationListItem,
  PaginationPrev,
  PaginationNext,
  PaginationFirst,
  PaginationLast,
  PaginationEllipsis,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { buttonVariants } from '@/components/button/types'
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
  // Reset to page 1 when size changes
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
        v-if="layoutItem === 'total' && showTotal && total !== undefined"
        data-slot="pagination-total"
        class="text-sm text-muted-foreground shrink-0"
      >
        共 {{ total }} 条
      </span>

      <!-- Page size selector -->
      <select
        v-if="layoutItem === 'sizes' && showSizeChanger"
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
        :disabled="disabled"
        :class="cn('mx-auto flex w-full justify-center')"
        @update:page="onPageChange"
      >
        <PaginationList
          v-slot="{ items: paginationItems }"
          data-slot="pagination-content"
          :class="cn('flex flex-row items-center gap-1')"
        >
          <!-- First page button -->
          <PaginationFirst
            v-if="hasLayout('prev')"
            data-slot="pagination-first"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronsLeft class="size-4" />
          </PaginationFirst>

          <!-- Previous page button -->
          <PaginationPrev
            v-if="hasLayout('prev')"
            data-slot="pagination-previous"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronLeft class="size-4" />
          </PaginationPrev>

          <!-- Page number items -->
          <template v-for="(paginationItem, index) in paginationItems" :key="index">
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

          <!-- Next page button -->
          <PaginationNext
            v-if="hasLayout('next')"
            data-slot="pagination-next"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronRight class="size-4" />
          </PaginationNext>

          <!-- Last page button -->
          <PaginationLast
            v-if="hasLayout('next')"
            data-slot="pagination-last"
            :disabled="disabled"
            :class="cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'size-9')"
          >
            <ChevronsRight class="size-4" />
          </PaginationLast>
        </PaginationList>
      </PaginationRoot>

      <!-- Jumper -->
      <div
        v-if="layoutItem === 'jumper' && jumper"
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
