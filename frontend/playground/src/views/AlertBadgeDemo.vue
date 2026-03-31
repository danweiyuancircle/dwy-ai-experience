<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const showDefault = ref(true)
const showDestructive = ref(true)
const showClosable = ref(true)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'alert-variants', label: 'Alert 变体' },
  { id: 'alert-closable', label: '可关闭 Alert' },
  { id: 'badge-variants', label: 'Badge 变体' },
  { id: 'badge-usage', label: 'Badge 使用场景' },
  { id: 'alert-props', label: 'Alert Props' },
  { id: 'alert-events', label: 'Alert Events' },
  { id: 'alert-slots', label: 'Alert Slots' },
  { id: 'badge-props', label: 'Badge Props' },
  { id: 'badge-slots', label: 'Badge Slots' },
]

const alertPropsData = [
  { name: 'variant', type: "'default' | 'destructive'", default: "'default'", description: '提示样式变体' },
  { name: 'title', type: 'string', default: '-', description: '提示标题' },
  { name: 'description', type: 'string', default: '-', description: '提示描述内容' },
  { name: 'closable', type: 'boolean', default: 'false', description: '是否显示关闭按钮' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const alertEventsData = [
  { name: 'close', params: '()', description: '点击关闭按钮时触发' },
]

const alertSlotsData = [
  { name: 'default', description: '自定义提示内容（替代 description prop）' },
]

const badgePropsData = [
  { name: 'variant', type: "'default' | 'secondary' | 'destructive' | 'outline'", default: "'default'", description: '徽标样式变体' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const badgeSlotsData = [
  { name: 'default', description: '徽标文字内容' },
]
</script>

<template>
  <ComponentDoc
    title="Alert & Badge"
    description="Alert 用于展示重要信息，Badge 用于状态标记和数量显示。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Alert 适用于页面内的重要信息提示，如操作成功/失败反馈、系统公告、警告信息等。Badge 适用于状态标记（在职/离职）、版本标识（Beta/弃用）、数量显示（未读消息数）等场景。</p>
    </section>

    <section id="alert-variants">
      <DemoBlock
        title="Alert 变体"
        description="支持 default 和 destructive 两种样式变体"
        code='<EAlert title="提示" description="这是一条普通提示信息。" />
<EAlert variant="destructive" title="错误" description="操作失败，请检查数据。" />'
      >
        <div class="space-y-3">
          <EAlert title="操作提示" description="您的数据已自动保存，最近保存时间：2 分钟前。" />
          <EAlert variant="destructive" title="操作失败" description="无法连接到服务器，请检查网络连接后重试。" />
        </div>
      </DemoBlock>
    </section>

    <section id="alert-closable">
      <DemoBlock
        title="可关闭 Alert"
        description="设置 closable 显示关闭按钮"
        code='<EAlert title="提示" description="点击右上角关闭" closable @close="visible = false" />'
      >
        <div class="space-y-3">
          <EAlert
            v-if="showDefault"
            title="信息提示"
            description="这是可以关闭的提示，点击右侧 × 关闭。"
            :closable="true"
            @close="showDefault = false"
          />
          <EAlert
            v-if="showDestructive"
            variant="destructive"
            title="警告信息"
            description="这是可以关闭的错误提示。"
            :closable="true"
            @close="showDestructive = false"
          />
          <div v-if="!showDefault && !showDestructive" class="space-y-2">
            <p class="text-sm text-muted-foreground">所有提示已关闭</p>
            <EButton size="sm" variant="outline" @click="() => { showDefault = true; showDestructive = true }">重新显示</EButton>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="badge-variants">
      <DemoBlock
        title="Badge 变体"
        description="4 种徽标样式：default、secondary、destructive、outline"
        code='<EBadge>默认</EBadge>
<EBadge variant="secondary">次要</EBadge>
<EBadge variant="destructive">危险</EBadge>
<EBadge variant="outline">描边</EBadge>'
      >
        <div class="flex flex-wrap gap-3">
          <EBadge>默认</EBadge>
          <EBadge variant="secondary">次要</EBadge>
          <EBadge variant="destructive">危险</EBadge>
          <EBadge variant="outline">描边</EBadge>
        </div>
      </DemoBlock>
    </section>

    <section id="badge-usage">
      <DemoBlock
        title="Badge 使用场景"
        description="常见的徽标应用场景"
      >
        <div class="space-y-4">
          <!-- 状态标签 -->
          <div class="flex flex-wrap gap-2">
            <EBadge>在职</EBadge>
            <EBadge variant="secondary">休假</EBadge>
            <EBadge variant="outline">兼职</EBadge>
            <EBadge variant="destructive">离职</EBadge>
          </div>
          <!-- 版本标签 -->
          <div class="flex flex-wrap gap-2">
            <EBadge variant="outline">v1.0.0</EBadge>
            <EBadge variant="secondary">Beta</EBadge>
            <EBadge variant="destructive">弃用</EBadge>
          </div>
          <!-- 与文字组合 -->
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium">未读消息</span>
            <EBadge variant="destructive">12</EBadge>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="alert-props">
      <h2 class="text-lg font-semibold mb-3">Alert API</h2>
      <PropsTable :data="alertPropsData" />
    </section>

    <section id="alert-events">
      <EventsTable :data="alertEventsData" />
    </section>

    <section id="alert-slots">
      <SlotsTable :data="alertSlotsData" />
    </section>

    <section id="badge-props">
      <h2 class="text-lg font-semibold mb-3">Badge API</h2>
      <PropsTable :data="badgePropsData" />
    </section>

    <section id="badge-slots">
      <SlotsTable :data="badgeSlotsData" />
    </section>
  </ComponentDoc>
</template>
