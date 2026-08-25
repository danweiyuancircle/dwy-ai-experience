<!--
  EDataPage 数据列表页组件
  组合 ETable + EPagination + 搜索框的通用列表页骨架
  仅关心"列 + 取数函数"，分页/搜索/loading 由内部统一处理
-->
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { cn } from '@/utils/cn'
import { EInput } from '../input'
import { EButton } from '../button'
import { ETable } from '../table'
import { EPagination } from '../pagination'
import type { EDataPageProps } from './types'

const props = withDefaults(defineProps<EDataPageProps>(), {
  searchable: true,
  pageSize: 10,
})

// 数据形状由业务决定，此处用 any 承载
const data = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const currentPageSize = ref(props.pageSize)
const keyword = ref('')
const loading = ref(false)

/**
 * 调用 fetchFn 拉取列表数据，失败时打 console 避免页面崩溃
 */
async function fetchData() {
  loading.value = true
  try {
    const result = await props.fetchFn({
      page: currentPage.value,
      pageSize: currentPageSize.value,
      keyword: keyword.value || undefined,
    })
    data.value = result.items
    total.value = result.total
  }
  catch (err) {
    console.error('EDataPage fetch error:', err)
  }
  finally {
    loading.value = false
  }
}

/** 触发搜索：回到首页再拉取 */
function handleSearch() {
  currentPage.value = 1
  fetchData()
}

/** 页码变化时重新拉取 */
function handlePageChange(page: number) {
  currentPage.value = page
  fetchData()
}

/** 每页条数变化时回到首页并重新拉取 */
function handlePageSizeChange(size: number) {
  currentPageSize.value = size
  currentPage.value = 1
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div
    data-slot="data-page"
    :class="cn('flex flex-col gap-4', props.class)"
  >
    <div v-if="searchable" class="flex items-center gap-2">
      <EInput
        v-model="keyword"
        placeholder="搜索..."
        class="max-w-xs"
        @keydown.enter="handleSearch"
      />
      <EButton @click="handleSearch">
        搜索
      </EButton>
    </div>

    <ETable
      :columns="columns"
      :data="data"
      :loading="loading"
    />

    <div class="flex items-center justify-between">
      <p class="text-sm text-muted-foreground">
        共 {{ total }} 条
      </p>
      <EPagination
        :total="total"
        :model-value="currentPage"
        :page-size="currentPageSize"
        :page-sizes="pageSizes"
        show-size-changer
        @update:model-value="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </div>
</template>
