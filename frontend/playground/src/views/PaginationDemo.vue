<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const page1 = ref(1)
const page2 = ref(3)
const page3 = ref(1)
const pageSize3 = ref(20)
const page4 = ref(1)
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Pagination 分页</h1>
    <p class="text-muted-foreground mb-6">数据分页组件，支持总数显示、页码大小切换、当前页控制。</p>

    <DemoBlock
      title="基础分页"
      description="最简单的分页控件"
      code='<EPagination v-model="page" :total="100" />'
    >
      <div class="space-y-3">
        <EPagination v-model="page1" :total="100" />
        <p class="text-sm text-muted-foreground">当前页：{{ page1 }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="显示总数"
      description="设置 showTotal 显示数据总条数"
      code='<EPagination v-model="page" :total="250" :pageSize="10" showTotal />'
    >
      <div class="space-y-3">
        <EPagination v-model="page2" :total="250" :pageSize="10" :showTotal="true" />
        <p class="text-sm text-muted-foreground">当前页：{{ page2 }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="可改变每页数量"
      description="设置 showSizeChanger 显示每页数量选择器"
      code='<EPagination
  v-model="page"
  :total="500"
  v-model:pageSize="pageSize"
  showSizeChanger
  showTotal
/>'
    >
      <div class="space-y-3">
        <EPagination
          v-model="page3"
          :total="500"
          v-model:pageSize="pageSize3"
          :showSizeChanger="true"
          :showTotal="true"
          :pageSizes="[10, 20, 50, 100]"
        />
        <p class="text-sm text-muted-foreground">当前页：{{ page3 }}，每页：{{ pageSize3 }} 条</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="带跳转分页"
      description="设置 jumper 和 layout 启用页码跳转输入框"
      code='<EPagination v-model="page" :total="500" jumper layout="total, prev, pager, next, jumper" />'
    >
      <div class="space-y-3">
        <EPagination
          v-model="page4"
          :total="500"
          jumper
          layout="total, prev, pager, next, jumper"
          :showTotal="true"
        />
        <p class="text-sm text-muted-foreground">当前页：{{ page4 }}</p>
      </div>
    </DemoBlock>
  </div>
</template>
