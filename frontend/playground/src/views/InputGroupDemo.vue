<script setup lang="ts">
import { ref } from 'vue'
import { Search, Mail, Globe, DollarSign } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const searchValue = ref('')
const emailValue = ref('')
const urlValue = ref('')
const priceValue = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'prefix', label: '前缀附加' },
  { id: 'suffix', label: '后缀附加' },
  { id: 'both', label: '前后缀组合' },
  { id: 'icon', label: '图标附加' },
  { id: 'group-props', label: 'EInputGroup Props' },
  { id: 'addon-props', label: 'EInputGroupAddon Props' },
  { id: 'slots', label: 'Slots' },
]

const groupPropsData = [
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const addonPropsData = [
  { name: 'align', type: "'inline-start' | 'inline-end' | 'block-start' | 'block-end'", default: "'inline-start'", description: '附加内容的对齐位置' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default (EInputGroup)', description: '放置 EInput 和 EInputGroupAddon' },
  { name: 'default (EInputGroupAddon)', description: '附加内容（文字、图标等）' },
]
</script>

<template>
  <ComponentDoc
    title="InputGroup 输入框组"
    description="为输入框添加前缀或后缀附加内容，常用于搜索框、URL 输入、金额输入等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在输入框前后添加说明性文字、图标或操作按钮的场景，如搜索框前加搜索图标、URL 输入框前加协议前缀、金额输入框后加货币单位等。</p>
    </section>

    <section id="prefix">
      <DemoBlock
        title="前缀附加"
        description="在输入框左侧添加图标或文字前缀"
        code='<EInputGroup>
  <EInputGroupAddon>
    <Search class="size-4" />
  </EInputGroupAddon>
  <EInput v-model="searchValue" placeholder="搜索..." />
</EInputGroup>'
      >
        <div class="space-y-4 max-w-sm">
          <EInputGroup>
            <EInputGroupAddon>
              <Search class="size-4" />
            </EInputGroupAddon>
            <EInput v-model="searchValue" placeholder="搜索..." />
          </EInputGroup>

          <EInputGroup>
            <EInputGroupAddon>
              <Mail class="size-4" />
            </EInputGroupAddon>
            <EInput v-model="emailValue" placeholder="输入邮箱地址" />
          </EInputGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="suffix">
      <DemoBlock
        title="后缀附加"
        description="在输入框右侧添加后缀说明"
        code='<EInputGroup>
  <EInput v-model="priceValue" placeholder="输入金额" />
  <EInputGroupAddon align="inline-end">.00</EInputGroupAddon>
</EInputGroup>'
      >
        <div class="space-y-4 max-w-sm">
          <EInputGroup>
            <EInput v-model="priceValue" placeholder="输入金额" />
            <EInputGroupAddon align="inline-end">.00</EInputGroupAddon>
          </EInputGroup>

          <EInputGroup>
            <EInput placeholder="输入域名" />
            <EInputGroupAddon align="inline-end">.com</EInputGroupAddon>
          </EInputGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="both">
      <DemoBlock
        title="前后缀组合"
        description="同时添加前缀和后缀"
        code='<EInputGroup>
  <EInputGroupAddon><DollarSign class="size-4" /></EInputGroupAddon>
  <EInput placeholder="0.00" />
  <EInputGroupAddon align="inline-end">USD</EInputGroupAddon>
</EInputGroup>'
      >
        <div class="space-y-4 max-w-sm">
          <EInputGroup>
            <EInputGroupAddon><DollarSign class="size-4" /></EInputGroupAddon>
            <EInput placeholder="0.00" />
            <EInputGroupAddon align="inline-end">USD</EInputGroupAddon>
          </EInputGroup>

          <EInputGroup>
            <EInputGroupAddon><Globe class="size-4" /></EInputGroupAddon>
            <EInput v-model="urlValue" placeholder="example.com" />
            <EInputGroupAddon align="inline-end">/path</EInputGroupAddon>
          </EInputGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="icon">
      <DemoBlock
        title="图标附加"
        description="使用图标作为前缀附加内容，提供视觉提示"
      >
        <div class="space-y-4 max-w-sm">
          <EInputGroup>
            <EInputGroupAddon>https://</EInputGroupAddon>
            <EInput placeholder="www.example.com" />
          </EInputGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="group-props">
      <h2 class="text-lg font-semibold mb-3">EInputGroup Props</h2>
      <PropsTable :data="groupPropsData" />
    </section>

    <section id="addon-props">
      <h2 class="text-lg font-semibold mb-3">EInputGroupAddon Props</h2>
      <PropsTable :data="addonPropsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
