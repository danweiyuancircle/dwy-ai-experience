<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref('')
const disabledValue = ref('')
const selectedUser = ref('')

const userOptions = [
  { label: '张三', value: 'zhangsan' },
  { label: '李四', value: 'lisi' },
  { label: '王五', value: 'wangwu' },
  { label: '赵六', value: 'zhaoliu' },
  { label: '孙七', value: 'sunqi' },
]

function handleSelect(option: { label: string; value: string }) {
  selectedUser.value = option.label
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'custom-prefix', label: '自定义前缀' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'string', default: "''", description: '输入框内容（支持 v-model）' },
  { name: 'options', type: 'MentionOption[]', default: '[]', description: '提及选项列表 { label, value }' },
  { name: 'prefix', type: 'string', default: "'@'", description: '触发提及的前缀字符' },
  { name: 'loading', type: 'boolean', default: 'false', description: '选项加载状态' },
  { name: 'placeholder', type: 'string', description: '占位文本' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '输入内容变化时触发' },
  { name: 'select', params: '(option: MentionOption)', description: '选中某个提及选项时触发' },
]

const slotsData = [
  { name: '—', description: '该组件暂无自定义插槽' },
]
</script>

<template>
  <ComponentDoc
    title="Mention 提及"
    description="在文本输入中通过特定前缀（如 @）触发用户/选项列表，选中后自动插入到文本中。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于评论、即时通讯、任务分配等需要 @提及用户 的场景。输入前缀字符后弹出匹配的选项列表，支持键盘上下选择和回车确认，选中后自动将用户名插入到输入框中。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="输入 @ 触发用户列表，支持模糊搜索和键盘导航"
        code='<EMention
  v-model="basicValue"
  :options="userOptions"
  placeholder="输入 @ 提及用户..."
  @select="handleSelect"
/>'
      >
        <div class="max-w-lg space-y-3">
          <EMention
            v-model="basicValue"
            :options="userOptions"
            placeholder="输入 @ 提及用户..."
            @select="handleSelect"
          />
          <div class="text-xs text-muted-foreground space-y-1">
            <p>输入内容：{{ basicValue || '（空）' }}</p>
            <p v-if="selectedUser">最近选中：{{ selectedUser }}</p>
            <p>提示：输入 <code class="bg-muted px-1 py-0.5 rounded">@</code> 后跟姓名首字母触发搜索，如 <code class="bg-muted px-1 py-0.5 rounded">@张</code></p>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="custom-prefix">
      <DemoBlock
        title="自定义前缀"
        description="通过 prefix 属性修改触发字符，如使用 # 触发标签选择"
        code='<EMention
  v-model="value"
  :options="tagOptions"
  prefix="#"
  placeholder="输入 # 选择标签..."
/>'
      >
        <div class="max-w-lg">
          <EMention
            :options="[
              { label: '重要', value: 'important' },
              { label: '紧急', value: 'urgent' },
              { label: '待办', value: 'todo' },
              { label: '已完成', value: 'done' },
            ]"
            prefix="#"
            placeholder="输入 # 选择标签..."
          />
          <p class="text-xs text-muted-foreground mt-2">输入 <code class="bg-muted px-1 py-0.5 rounded">#</code> 触发标签列表</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="禁用后输入框不可编辑"
        code='<EMention
  v-model="disabledValue"
  :options="userOptions"
  disabled
  placeholder="已禁用"
/>'
      >
        <div class="max-w-lg">
          <EMention
            v-model="disabledValue"
            :options="userOptions"
            disabled
            placeholder="已禁用"
          />
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
