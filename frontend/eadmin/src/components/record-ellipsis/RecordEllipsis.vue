<!--
  表格里的长文本。
  格子里截断时可悬停或键盘聚焦看全文；完整可见文本不占用 Tab 停靠。
-->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ETooltip } from '@dwydev/eui'

defineOptions({ name: 'RecordEllipsis' })

const props = withDefaults(
  defineProps<{
    /** 原文。空则显示占位。示例：``'alice@example.com'``。 */
    text?: string | number | null
    /** 空值占位。默认 ``'—'``。示例：``'-'``。 */
    emptyText?: string
    /** 加在提示层上的类。长文案需要限宽时传入。 */
    tooltipClass?: string
  }>(),
  { emptyText: '—' },
)

/** 空值换成占位，避免格子一片空白。 */
const display = computed(() => {
  if (props.text === null || props.text === undefined || props.text === '') return props.emptyText
  return String(props.text)
})

/** 占位和短横线没有全文可看。 */
const hasContent = computed(() => display.value !== props.emptyText && display.value !== '-' && display.value !== '—')
const textElement = ref<HTMLElement>()
const truncated = ref(false)
const showTip = computed(() => hasContent.value && truncated.value)
let resizeObserver: ResizeObserver | undefined

function onKeydown(event: KeyboardEvent) {
  if (!showTip.value || (event.key !== 'Enter' && event.key !== ' ')) return
  event.preventDefault()
  event.stopPropagation()
  if (!event.repeat) (event.currentTarget as HTMLElement).click()
}

function onClick(event: MouseEvent) {
  if (showTip.value) event.stopPropagation()
}

function measure() {
  const element = textElement.value
  truncated.value = !!element && element.scrollWidth > element.clientWidth
}

function observeText() {
  if (!textElement.value) return
  resizeObserver?.disconnect()
  resizeObserver?.observe(textElement.value)
  measure()
}

// ETooltip 在触屏与桌面之间切换时会替换触发节点，需要跟随新节点重新测量。
watch([textElement, display], observeText, { flush: 'post' })
onMounted(() => {
  window.addEventListener('resize', measure)
  if (typeof ResizeObserver !== 'undefined') resizeObserver = new ResizeObserver(measure)
  observeText()
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', measure)
  resizeObserver?.disconnect()
})
</script>

<template>
  <ETooltip :content="display" :disabled="!showTip" :class="tooltipClass">
    <span
      ref="textElement"
      class="block min-w-0 truncate rounded-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
      :class="hasContent ? undefined : 'text-muted-foreground'"
      :tabindex="showTip ? 0 : undefined"
      :role="showTip ? 'button' : undefined"
      :aria-label="showTip ? `查看全文：${display}` : undefined"
      @keydown="onKeydown"
      @click="onClick"
    >
      {{ display }}
    </span>
  </ETooltip>
</template>
