<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const confirmOpen = ref(false)
const confirmWarningOpen = ref(false)
const confirmErrorOpen = ref(false)
const confirmResult = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'types', label: '危险等级' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '对话框是否打开（支持 v-model:open）' },
  { name: 'title', type: 'string', description: '对话框标题' },
  { name: 'message', type: 'string', description: '确认提示消息' },
  { name: 'type', type: "'info' | 'warning' | 'error'", default: "'info'", description: '危险等级，影响图标颜色和确认按钮样式' },
  { name: 'confirmText', type: 'string', default: "'确认'", description: '确认按钮文字' },
  { name: 'cancelText', type: 'string', default: "'取消'", description: '取消按钮文字' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '打开/关闭状态变化时触发' },
  { name: 'confirm', params: '()', description: '点击确认按钮时触发' },
  { name: 'cancel', params: '()', description: '点击取消按钮时触发' },
]
</script>

<template>
  <ComponentDoc
    title="ConfirmDialog 确认对话框"
    description="支持 info / warning / error 三种危险等级的确认对话框，用于二次确认操作。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于删除、清空、提交等需要二次确认的操作场景。通过 type 属性区分操作的危险等级：info 用于普通确认，warning 用于有风险的操作，error 用于不可逆的危险操作。不同等级显示不同颜色的图标和确认按钮。</p>
    </section>

    <section id="types">
      <DemoBlock
        title="危险等级"
        description="支持 info / warning / error 三种危险等级"
        code='<EConfirmDialog
  v-model:open="open"
  type="warning"
  title="确认删除"
  message="此操作不可逆，确定要删除吗？"
  @confirm="handleConfirm"
/>'
      >
        <div class="flex flex-wrap gap-3">
          <EButton variant="outline" @click="confirmOpen = true">信息确认</EButton>
          <EButton variant="secondary" @click="confirmWarningOpen = true">警告确认</EButton>
          <EButton variant="destructive" @click="confirmErrorOpen = true">危险确认</EButton>
        </div>
        <p v-if="confirmResult" class="text-sm mt-2 text-muted-foreground">操作结果：{{ confirmResult }}</p>

        <EConfirmDialog
          v-model:open="confirmOpen"
          type="info"
          title="确认操作"
          message="您确定要执行此操作吗？这将影响所有相关数据。"
          @confirm="() => { confirmResult = '点击了确认（info）'; confirmOpen = false }"
          @cancel="() => { confirmResult = '点击了取消'; confirmOpen = false }"
        />
        <EConfirmDialog
          v-model:open="confirmWarningOpen"
          type="warning"
          title="注意"
          message="此操作将清空所有缓存数据，确定继续吗？"
          confirm-text="继续"
          @confirm="() => { confirmResult = '点击了继续（warning）'; confirmWarningOpen = false }"
          @cancel="() => { confirmResult = '点击了取消'; confirmWarningOpen = false }"
        />
        <EConfirmDialog
          v-model:open="confirmErrorOpen"
          type="error"
          title="危险操作"
          message="此操作将永久删除所有数据，无法恢复。请确认您已知晓此风险。"
          confirm-text="我已知晓，继续删除"
          cancel-text="取消"
          @confirm="() => { confirmResult = '点击了删除（error）'; confirmErrorOpen = false }"
          @cancel="() => { confirmResult = '点击了取消'; confirmErrorOpen = false }"
        />
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Slots</h2>
      <p class="text-sm text-muted-foreground">该组件无自定义插槽。</p>
    </section>
  </ComponentDoc>
</template>
