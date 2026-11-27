<!--
  档案页壳：返回、身份卡、下面的分区。
  身份卡只排标题、徽章、说明、操作。套餐、账单等分区由页面放进默认插槽。
  没有 title 时不画身份卡，用来放「没有这个人」的空态。
-->
<script setup lang="ts">
import { useSlots } from 'vue'
import { EButton, ECard } from '@dwydev/eui'

defineOptions({ name: 'RecordProfile' })

defineProps<{
  /** 身份卡标题。不传则不画卡。示例：``'alice'``。 */
  title?: string
  /** 返回按钮文案。不传则没有返回。示例：``'返回用户列表'``。 */
  backLabel?: string
}>()

const emit = defineEmits<{
  /** 点返回。去哪由页面决定。 */
  back: []
}>()

const slots = useSlots()
</script>

<template>
  <div class="flex flex-col gap-6">
    <div v-if="backLabel" class="flex flex-wrap items-center gap-2">
      <!-- type=button：避免将来套进表单时被当成提交。 -->
      <EButton size="sm" variant="outline" type="button" @click="emit('back')">{{ backLabel }}</EButton>
    </div>
    <ECard v-if="title" :title="title">
      <div class="flex flex-col gap-3">
        <div v-if="slots.meta" class="flex flex-wrap items-center gap-2">
          <slot name="meta" />
        </div>
        <p v-if="slots.description" class="text-sm text-muted-foreground">
          <slot name="description" />
        </p>
        <div v-if="slots.actions" class="flex flex-wrap gap-2">
          <slot name="actions" />
        </div>
      </div>
    </ECard>
    <slot />
  </div>
</template>
