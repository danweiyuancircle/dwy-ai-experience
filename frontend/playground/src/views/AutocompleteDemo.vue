<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref('')

const allSuggestions = [
  { label: 'Vue.js', value: 'vue' },
  { label: 'Vue Router', value: 'vue-router' },
  { label: 'Vuex', value: 'vuex' },
  { label: 'Vite', value: 'vite' },
  { label: 'Vitest', value: 'vitest' },
  { label: 'React', value: 'react' },
  { label: 'React Router', value: 'react-router' },
  { label: 'Redux', value: 'redux' },
  { label: 'Next.js', value: 'nextjs' },
  { label: 'Nuxt.js', value: 'nuxtjs' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Tailwind CSS', value: 'tailwindcss' },
]

async function fetchSuggestions(query: string) {
  // 模拟异步请求延迟
  await new Promise((resolve) => setTimeout(resolve, 200))
  if (!query) return []
  return allSuggestions.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase()),
  )
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string', default: "''", description: '绑定值' },
  { name: 'fetchSuggestions', type: '(query: string) => Promise<AutocompleteOption[]>', default: '—', description: '异步获取建议列表的函数' },
  { name: 'debounce', type: 'number', default: '—', description: '输入防抖延迟（毫秒）' },
  { name: 'placeholder', type: 'string', default: '—', description: '输入框占位文本' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: 'v-model 绑定值变化时触发' },
  { name: 'select', params: '(option: AutocompleteOption)', description: '选中建议项时触发' },
  { name: 'change', params: '(value: string)', description: '值改变时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Autocomplete 自动补全"
    description="输入时自动联想补全，通过异步函数获取建议列表。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于搜索框联想、地址输入补全、标签快速输入等需要根据用户输入动态提供建议的场景。通过 fetchSuggestions 异步获取候选项，支持 debounce 防抖。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="传入 fetchSuggestions 异步函数，输入时自动显示建议列表"
        code='<EAutocomplete
  v-model="value"
  :fetchSuggestions="fetchSuggestions"
  placeholder="输入前端框架名称"
/>'
      >
        <div class="space-y-2 max-w-sm">
          <EAutocomplete
            v-model="basicValue"
            :fetch-suggestions="fetchSuggestions"
            placeholder="输入前端框架名称，如 vue、react"
          />
          <p class="text-sm text-muted-foreground">当前值：{{ basicValue || '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止交互"
        code='<EAutocomplete disabled placeholder="禁用状态" />'
      >
        <div class="max-w-sm">
          <EAutocomplete disabled placeholder="禁用状态" />
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
