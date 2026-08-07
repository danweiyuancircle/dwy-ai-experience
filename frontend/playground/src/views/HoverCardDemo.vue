<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'openDelay', type: 'number', default: '700', description: '鼠标悬停后延迟打开的毫秒数' },
  { name: 'closeDelay', type: 'number', default: '300', description: '鼠标移开后延迟关闭的毫秒数' },
  { name: 'class', type: 'string', description: '自定义内容区域的 CSS 类名' },
]

const slotsData = [
  { name: 'trigger', description: '触发器内容，鼠标悬停后弹出卡片' },
  { name: 'default', description: '悬浮卡片的主体内容' },
]
</script>

<template>
  <ComponentDoc
    title="HoverCard 悬浮卡片"
    description="鼠标悬停时弹出的信息卡片，用于预览用户资料、链接摘要等内容，无需点击即可查看。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于鼠标悬停展示补充信息的场景，如用户头像悬停显示资料卡片、链接悬停显示页面摘要等。与 Tooltip 的区别在于 HoverCard 可以承载更丰富的内容和交互元素。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="鼠标悬停在触发元素上，弹出用户信息卡片"
        code='<EHoverCard>
  <template #trigger>
    <a href="#" class="underline">@张三</a>
  </template>
  <div class="space-y-2">
    <h4 class="text-sm font-semibold">张三</h4>
    <p class="text-sm text-muted-foreground">前端开发工程师，热爱开源。</p>
    <p class="text-xs text-muted-foreground">加入于 2024 年 3 月</p>
  </div>
</EHoverCard>'
      >
        <div class="flex items-center gap-6">
          <EHoverCard>
            <template #trigger>
              <a href="#" class="text-sm font-medium underline underline-offset-4" @click.prevent>@张三</a>
            </template>
            <div class="flex gap-4">
              <EAvatar fallback="张" class="size-10" />
              <div class="space-y-1">
                <h4 class="text-sm font-semibold">张三</h4>
                <p class="text-sm text-muted-foreground">前端开发工程师，热爱开源。</p>
                <div class="flex items-center pt-1">
                  <span class="text-xs text-muted-foreground">加入于 2024 年 3 月</span>
                </div>
              </div>
            </div>
          </EHoverCard>

          <EHoverCard :open-delay="200" :close-delay="100">
            <template #trigger>
              <a href="#" class="text-sm font-medium underline underline-offset-4" @click.prevent>@李四</a>
            </template>
            <div class="flex gap-4">
              <EAvatar fallback="李" class="size-10" />
              <div class="space-y-1">
                <h4 class="text-sm font-semibold">李四</h4>
                <p class="text-sm text-muted-foreground">全栈工程师，专注于 Vue 和 Node.js。</p>
                <div class="flex items-center pt-1">
                  <span class="text-xs text-muted-foreground">加入于 2023 年 8 月</span>
                </div>
              </div>
            </div>
          </EHoverCard>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
