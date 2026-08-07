<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const selected = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'composition', label: '组合子组件' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string', default: "''", description: '当前选中项的值' },
  { name: 'class', type: 'string', default: '—', description: '根容器自定义类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '选中项变化时触发' },
]

const compositionData = [
  { name: 'ECommand', description: '根容器，管理过滤状态' },
  { name: 'ECommandInput', description: '搜索输入框' },
  { name: 'ECommandList', description: '可滚动列表容器' },
  { name: 'ECommandEmpty', description: '无匹配结果时展示' },
  { name: 'ECommandGroup', description: '选项分组' },
  { name: 'ECommandItem', description: '可选条目' },
  { name: 'ECommandSeparator', description: '分隔线' },
  { name: 'ECommandShortcut', description: '快捷键提示文案' },
]
</script>

<template>
  <ComponentDoc
    title="Command 命令面板"
    description="可搜索的命令/选项面板，类似 VS Code 命令面板，由 ECommand 族子组件组合使用。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">
        适用于应用内命令搜索、快捷跳转、带分组的选项选择。通常放在 Dialog 内作为全局命令面板。
      </p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="输入关键词过滤，点击条目选中"
        code='<ECommand v-model="selected">
  <ECommandInput placeholder="搜索命令..." />
  <ECommandList>
    <ECommandEmpty>无结果</ECommandEmpty>
    <ECommandGroup heading="建议">
      <ECommandItem value="calendar">日历</ECommandItem>
      <ECommandItem value="emoji">表情</ECommandItem>
    </ECommandGroup>
  </ECommandList>
</ECommand>'
      >
        <ECommand v-model="selected" class="w-full max-w-md rounded-lg border shadow-md">
          <ECommandInput placeholder="搜索命令..." />
          <ECommandList>
            <ECommandEmpty>无结果</ECommandEmpty>
            <ECommandGroup heading="建议">
              <ECommandItem value="calendar">日历</ECommandItem>
              <ECommandItem value="emoji">
                表情
                <ECommandShortcut>⌘E</ECommandShortcut>
              </ECommandItem>
              <ECommandItem value="calculator">计算器</ECommandItem>
            </ECommandGroup>
            <ECommandSeparator />
            <ECommandGroup heading="设置">
              <ECommandItem value="profile">个人资料</ECommandItem>
              <ECommandItem value="billing">账单</ECommandItem>
            </ECommandGroup>
          </ECommandList>
        </ECommand>
        <p v-if="selected" class="mt-3 text-sm text-muted-foreground">
          已选：{{ selected }}
        </p>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Props（ECommand）</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Events</h2>
      <EventsTable :data="eventsData" />
    </section>

    <section id="composition">
      <h2 class="text-lg font-semibold mb-3">组合子组件</h2>
      <SlotsTable :data="compositionData" />
    </section>
  </ComponentDoc>
</template>
