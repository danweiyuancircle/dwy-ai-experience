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

const data = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const currentPageSize = ref(props.pageSize)
const keyword = ref('')
const loading = ref(false)

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

function handleSearch() {
  currentPage.value = 1
  fetchData()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchData()
}

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
        @update:model-value="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </div>
</template>
