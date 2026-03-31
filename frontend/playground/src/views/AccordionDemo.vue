<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const singleValue = ref('item1')
const multipleValue = ref<string[]>(['faq1', 'faq3'])

const basicItems = [
  { key: 'item1', title: '什么是 EUI？' },
  { key: 'item2', title: '如何安装和使用？' },
  { key: 'item3', title: '支持哪些浏览器？' },
  { key: 'item4', title: '是否支持暗色模式？' },
]

const faqItems = [
  { key: 'faq1', title: '如何自定义组件主题色？' },
  { key: 'faq2', title: 'EUI 与其他 UI 库的区别？' },
  { key: 'faq3', title: '是否支持 SSR（服务端渲染）？' },
  { key: 'faq4', title: '遇到问题如何获得帮助？', disabled: true },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Accordion 手风琴</h1>
    <p class="text-muted-foreground mb-6">折叠面板组件，支持单选展开和多选展开两种模式。</p>

    <DemoBlock
      title="单选手风琴（默认）"
      description="每次只能展开一个面板"
      code='<EAccordion v-model="value" :items="items">
  <template #item1>内容一</template>
</EAccordion>'
    >
      <EAccordion v-model="singleValue" :items="basicItems">
        <template #item1>
          <p class="text-sm text-muted-foreground">
            EUI 是一个基于 Vue 3 + Tailwind CSS v4 构建的现代化组件库，提供 91+ 个可复用 UI 组件，专为企业级应用设计。
          </p>
        </template>
        <template #item2>
          <div class="space-y-2 text-sm text-muted-foreground">
            <p>通过 pnpm 安装：</p>
            <code class="bg-muted px-2 py-1 rounded text-xs block">pnpm add @danweiyuan/eui</code>
            <p>在 main.ts 中引入：</p>
            <code class="bg-muted px-2 py-1 rounded text-xs block">import EUI from '@danweiyuan/eui'</code>
          </div>
        </template>
        <template #item3>
          <p class="text-sm text-muted-foreground">
            支持所有现代浏览器，包括 Chrome、Firefox、Safari、Edge 最新版本。不支持 IE11。
          </p>
        </template>
        <template #item4>
          <p class="text-sm text-muted-foreground">
            是的，EUI 内置了完整的暗色模式支持，通过 CSS 变量实现主题切换，无需额外配置。
          </p>
        </template>
      </EAccordion>
      <p class="text-sm text-muted-foreground mt-2">当前展开：{{ singleValue }}</p>
    </DemoBlock>

    <DemoBlock
      title="多选手风琴"
      description="设置 multiple 允许同时展开多个面板"
      code='<EAccordion v-model="value" :items="items" :multiple="true" />'
    >
      <EAccordion v-model="multipleValue" :items="faqItems" :multiple="true">
        <template #faq1>
          <p class="text-sm text-muted-foreground">
            在项目的 CSS 变量中修改 --primary 等设计 token，所有组件会自动应用新的主题色。
          </p>
        </template>
        <template #faq2>
          <p class="text-sm text-muted-foreground">
            EUI 专注于企业级中后台场景，内置业务组件（如 EDataPage、EFormDialog），减少重复代码。
          </p>
        </template>
        <template #faq3>
          <p class="text-sm text-muted-foreground">
            部分支持，核心组件可在 SSR 环境下使用，具体请参考文档中的 SSR 指南。
          </p>
        </template>
        <template #faq4>
          <p class="text-sm text-muted-foreground">（此项已禁用）</p>
        </template>
      </EAccordion>
    </DemoBlock>
  </div>
</template>
