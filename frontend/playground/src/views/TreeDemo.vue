<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const checkedKeys = ref<(string | number)[]>(['file1', 'file2'])
const expandedKeys = ref<(string | number)[]>(['root', 'src'])
const treeSelectValue = ref<string | number>('')

const treeData = [
  {
    key: 'root',
    label: '项目根目录',
    children: [
      {
        key: 'src',
        label: 'src',
        children: [
          { key: 'main', label: 'main.ts' },
          { key: 'app', label: 'App.vue' },
          {
            key: 'components',
            label: 'components',
            children: [
              { key: 'button', label: 'EButton.vue' },
              { key: 'input', label: 'EInput.vue' },
            ],
          },
        ],
      },
      {
        key: 'public',
        label: 'public',
        children: [
          { key: 'favicon', label: 'favicon.ico' },
        ],
      },
      { key: 'pkg', label: 'package.json' },
    ],
  },
]

const orgData = [
  {
    key: 'company',
    label: '公司',
    children: [
      {
        key: 'tech',
        label: '技术部',
        children: [
          { key: 'frontend', label: '前端组' },
          { key: 'backend', label: '后端组' },
          { key: 'devops', label: '运维组' },
        ],
      },
      {
        key: 'product',
        label: '产品部',
        children: [
          { key: 'pm', label: '产品经理' },
          { key: 'design', label: '设计组' },
        ],
      },
      {
        key: 'ops',
        label: '运营部',
        disabled: true,
      },
    ],
  },
]

const flatData = [
  { key: 'frontend', label: '前端开发' },
  { key: 'backend', label: '后端开发' },
  { key: 'fullstack', label: '全栈开发' },
  { key: 'mobile', label: '移动端开发' },
  { key: 'devops', label: '运维工程师' },
]

const filterQuery = ref('')
const filterMethod = (query: string, node: { label: string }) => {
  return node.label.toLowerCase().includes(query.toLowerCase())
}
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Tree 树形控件</h1>
    <p class="text-muted-foreground mb-6">树形数据展示组件，支持展开/折叠、复选框选择、禁用节点等。</p>

    <DemoBlock
      title="基础树形结构"
      description="展示文件目录结构"
      code='<ETree :data="treeData" defaultExpandAll />'
    >
      <ETree :data="treeData" :expanded-keys="expandedKeys" @update:expandedKeys="expandedKeys = $event" />
    </DemoBlock>

    <DemoBlock
      title="可勾选树"
      description="设置 checkable 启用复选框模式"
      code='<ETree :data="data" checkable v-model="checkedKeys" />'
    >
      <div class="flex gap-4">
        <ETree
          :data="orgData"
          :checkable="true"
          v-model="checkedKeys"
          class="flex-1"
        />
        <div class="flex-1 space-y-1">
          <p class="text-sm font-medium">已选节点：</p>
          <div v-if="checkedKeys.length > 0" class="flex flex-wrap gap-1">
            <EBadge v-for="key in checkedKeys" :key="key" variant="secondary">{{ key }}</EBadge>
          </div>
          <p v-else class="text-sm text-muted-foreground">未选择任何节点</p>
        </div>
      </div>
    </DemoBlock>

    <DemoBlock
      title="TreeSelect 下拉树"
      description="以下拉形式展示的树选择器"
      code='<ETreeSelect v-model="value" :data="treeData" placeholder="请选择" />'
    >
      <div class="space-y-3 max-w-sm">
        <ETreeSelect v-model="treeSelectValue" :data="orgData" placeholder="请选择部门" />
        <p class="text-sm text-muted-foreground">已选：{{ treeSelectValue || '(未选择)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="全部展开"
      description="设置 defaultExpandAll 默认展开所有节点"
      code='<ETree :data="data" :defaultExpandAll="true" />'
    >
      <ETree :data="orgData" :default-expand-all="true" />
    </DemoBlock>

    <DemoBlock
      title="可拖拽树"
      description="设置 draggable 启用节点拖拽排序"
      code='<ETree :data="treeData" draggable defaultExpandAll />'
    >
      <ETree :data="treeData" draggable :default-expand-all="true" />
    </DemoBlock>

    <DemoBlock
      title="可搜索树"
      description="通过 filter-query 和 filter-method 实现节点搜索过滤"
      code='<EInput v-model="filterQuery" placeholder="输入关键词搜索" />
<ETree :data="treeData" :filter-query="filterQuery" :filter-method="filterMethod" defaultExpandAll />'
    >
      <div class="space-y-3">
        <EInput v-model="filterQuery" placeholder="输入关键词搜索节点..." />
        <ETree
          :data="treeData"
          :filter-query="filterQuery"
          :filter-method="filterMethod"
          :default-expand-all="true"
        />
      </div>
    </DemoBlock>
  </div>
</template>
