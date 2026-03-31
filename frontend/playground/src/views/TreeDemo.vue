<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

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

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础树形结构' },
  { id: 'checkable', label: '可勾选树' },
  { id: 'tree-select', label: 'TreeSelect 下拉树' },
  { id: 'expand-all', label: '全部展开' },
  { id: 'draggable', label: '可拖拽树' },
  { id: 'filter', label: '可搜索树' },
  { id: 'tree-props', label: 'Tree Props' },
  { id: 'tree-events', label: 'Tree Events' },
  { id: 'tree-slots', label: 'Tree Slots' },
  { id: 'tree-select-props', label: 'TreeSelect Props' },
  { id: 'tree-select-events', label: 'TreeSelect Events' },
]

const treePropsData = [
  { name: 'data', type: 'TreeNode[]', default: '[]', description: '树形数据源' },
  { name: 'modelValue', type: '(string | number)[]', default: '[]', description: '勾选的节点 key 数组（v-model）' },
  { name: 'checkable', type: 'boolean', default: 'false', description: '是否启用复选框模式' },
  { name: 'expandedKeys', type: '(string | number)[]', default: '[]', description: '当前展开的节点 key 数组（v-model）' },
  { name: 'defaultExpandAll', type: 'boolean', default: 'false', description: '是否默认展开所有节点' },
  { name: 'lazy', type: 'boolean', default: 'false', description: '是否启用懒加载模式' },
  { name: 'loadFn', type: '(node: TreeNode) => Promise<TreeNode[]>', default: '-', description: '懒加载子节点的异步函数' },
  { name: 'draggable', type: 'boolean', default: 'false', description: '是否允许拖拽排序节点' },
  { name: 'filterMethod', type: '(query: string, node: TreeNode) => boolean', default: '-', description: '自定义过滤函数' },
  { name: 'filterQuery', type: 'string', default: '-', description: '搜索关键词，非空时启用过滤' },
  { name: 'checkStrictly', type: 'boolean', default: 'false', description: '父子节点选中状态是否互不关联' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const treeEventsData = [
  { name: 'update:modelValue', params: '(keys: (string | number)[])', description: '勾选状态变化时触发' },
  { name: 'update:expandedKeys', params: '(keys: (string | number)[])', description: '展开状态变化时触发' },
  { name: 'check', params: '(key: string | number, checked: boolean)', description: '节点勾选/取消时触发' },
  { name: 'select', params: '(key: string | number)', description: '点击选中节点时触发' },
  { name: 'node-drop', params: "(dragNode: TreeNode, dropNode: TreeNode, position: 'before' | 'inner' | 'after')", description: '拖拽放置节点时触发' },
]

const treeSlotsData = [
  { name: 'default', description: '自定义节点内容，参数 { node }' },
  { name: 'icon', description: '自定义节点图标' },
]

const treeSelectPropsData = [
  { name: 'modelValue', type: 'string | number | (string | number)[]', default: '-', description: '选中值（v-model）' },
  { name: 'data', type: 'TreeNode[]', default: '[]', description: '树形数据源' },
  { name: 'placeholder', type: 'string', default: '-', description: '占位文本' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否多选' },
  { name: 'checkable', type: 'boolean', default: 'false', description: '是否启用复选框模式' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const treeSelectEventsData = [
  { name: 'update:modelValue', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发' },
  { name: 'change', params: '(value: string | number | (string | number)[] | undefined)', description: '选中值变化时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Tree 树形控件"
    description="树形数据展示组件，支持展开/折叠、复选框选择、禁用节点等。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于展示具有层级关系的数据结构，如文件目录、组织架构、分类体系等。支持复选框多选、节点拖拽排序、关键词搜索过滤、懒加载子节点等功能。配合 TreeSelect 可实现下拉树选择器。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础树形结构"
        description="展示文件目录结构"
        code='<ETree :data="treeData" defaultExpandAll />'
      >
        <ETree :data="treeData" :expanded-keys="expandedKeys" @update:expandedKeys="expandedKeys = $event" />
      </DemoBlock>
    </section>

    <section id="checkable">
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
    </section>

    <section id="tree-select">
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
    </section>

    <section id="expand-all">
      <DemoBlock
        title="全部展开"
        description="设置 defaultExpandAll 默认展开所有节点"
        code='<ETree :data="data" :defaultExpandAll="true" />'
      >
        <ETree :data="orgData" :default-expand-all="true" />
      </DemoBlock>
    </section>

    <section id="draggable">
      <DemoBlock
        title="可拖拽树"
        description="设置 draggable 启用节点拖拽排序"
        code='<ETree :data="treeData" draggable defaultExpandAll />'
      >
        <ETree :data="treeData" draggable :default-expand-all="true" />
      </DemoBlock>
    </section>

    <section id="filter">
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
    </section>

    <section id="tree-props">
      <h2 class="text-lg font-semibold mb-3">Tree Props</h2>
      <PropsTable :data="treePropsData" />
    </section>

    <section id="tree-events">
      <h2 class="text-lg font-semibold mb-3">Tree Events</h2>
      <EventsTable :data="treeEventsData" />
    </section>

    <section id="tree-slots">
      <h2 class="text-lg font-semibold mb-3">Tree Slots</h2>
      <SlotsTable :data="treeSlotsData" />
    </section>

    <section id="tree-select-props">
      <h2 class="text-lg font-semibold mb-3">TreeSelect Props</h2>
      <PropsTable :data="treeSelectPropsData" />
    </section>

    <section id="tree-select-events">
      <h2 class="text-lg font-semibold mb-3">TreeSelect Events</h2>
      <EventsTable :data="treeSelectEventsData" />
    </section>
  </ComponentDoc>
</template>
