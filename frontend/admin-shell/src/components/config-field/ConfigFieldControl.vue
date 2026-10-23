<!--
  按字段种类画一个控件。
  字节值对外仍是字节数。单位只影响输入框里的数字，换单位不改已存的字节。
  换算函数由页面传入，这里不认 B/KB/MB。
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { EDatePicker, EInput, ENumberField, ESelect, ESwitch } from '@dwydev/eui'
import type { ConfigFieldSpec } from './types'

defineOptions({ name: 'ConfigFieldControl' })

const props = defineProps<{
  /** 当前存的值。byte 时是字节数。示例：``524288000``。 */
  modelValue: unknown
  /** 控件描述。 */
  spec: ConfigFieldSpec
  /**
   * 字节字段当前单位。
   * 别的种类忽略。没传时按 MB 显示。示例：``'MB'``。
   */
  unit?: string
}>()

/** 秒数升到能整除的最大单位。90 秒保持秒，避免写成 1.5 分钟。 */
const DURATION_DIV: Record<string, number> = { 秒: 1, 分钟: 60, 小时: 3600, 天: 86400 }
const DURATION_OPTIONS = [
  { label: '秒', value: '秒' },
  { label: '分钟', value: '分钟' },
  { label: '小时', value: '小时' },
  { label: '天', value: '天' },
]

/**
 * 选一个能整除的大单位。
 * @param seconds 秒数。取值 ``[0, ∞)``。示例：``900``。
 * @returns 单位。枚举 ``秒/分钟/小时/天``。示例：``'分钟'``。
 */
function pickDurationUnit(seconds: number): string {
  if (seconds >= 86400 && seconds % 86400 === 0) return '天'
  if (seconds >= 3600 && seconds % 3600 === 0) return '小时'
  if (seconds >= 60 && seconds % 60 === 0) return '分钟'
  return '秒'
}

/** 时长当前单位。外部整值替换（恢复默认）才重选，避免用户刚换的单位被弹回去。 */
const durationUnit = ref('秒')
let durationFromInput = false

watch(
  () => props.modelValue,
  (value) => {
    if (props.spec.kind !== 'duration') return
    if (durationFromInput) {
      durationFromInput = false
      return
    }
    if (typeof value === 'number') durationUnit.value = pickDurationUnit(value)
  },
  { immediate: true },
)

const emit = defineEmits<{
  /** 存盘值变化。byte 时仍是字节。 */
  'update:modelValue': [value: unknown]
  /** 字节单位变化。不改已存字节。 */
  'update:unit': [unit: string]
}>()

/** 父级还没写入单位时按 MB，和配置页原来的默认一致。 */
const activeUnit = computed(() => props.unit || 'MB')

/** 换算齐了才按体积画。缺函数时退回普通数字，避免静默把字节当 MB。 */
const isByte = computed(() =>
  props.spec.kind === 'byte' && props.spec.fromBytes !== undefined && props.spec.toBytes !== undefined,
)

/** 体积框里给用户看的数字。 */
const byteAmount = computed(() => {
  const fromBytes = props.spec.fromBytes
  if (!fromBytes) return 0
  return fromBytes(Number(props.modelValue ?? 0), activeUnit.value)
})

/**
 * 上下限从字节换到当前单位。没写界限就不管。
 * @param bytes 字节界限。空表示没有这一端。
 * @returns 当前单位下的数字。没有界限时是 undefined。
 */
function byteBound(bytes: number | null | undefined): number | undefined {
  const fromBytes = props.spec.fromBytes
  if (bytes == null || !fromBytes) return undefined
  return fromBytes(bytes, activeUnit.value)
}

/**
 * 体积框改数字。写回的是字节。
 * @param amount 当前单位下的数字。清空按 0。
 */
function onByteAmount(amount: number | null) {
  const toBytes = props.spec.toBytes
  if (!toBytes) return
  emit('update:modelValue', toBytes(Number(amount ?? 0), activeUnit.value))
}

/**
 * 换单位。只改显示刻度，已存字节不动。
 * @param unit 下拉值。多选和空值忽略。
 */
function onUnit(unit: string | number | (string | number)[] | undefined) {
  if (typeof unit !== 'string' || unit === '') return
  emit('update:unit', unit)
}

/**
 * 枚举改值。下拉只认单个字符串。
 * @param value 选中项。
 */
function onEnum(value: string | number | (string | number)[] | undefined) {
  if (typeof value !== 'string' && typeof value !== 'number') return
  emit('update:modelValue', String(value))
}

/**
 * 文本框收成字符串。
 * @param value 输入值。
 */
function onText(value: string | number) {
  emit('update:modelValue', String(value ?? ''))
}

/** 时长框里给用户看的数字。 */
const durationAmount = computed(() => {
  const div = DURATION_DIV[durationUnit.value] ?? 1
  return Number(props.modelValue ?? 0) / div
})

/**
 * 上下限从秒换到当前单位。
 * @param seconds 秒。空表示没有这一端。
 * @returns 当前单位下的数字。
 */
function durationBound(seconds: number | null | undefined): number | undefined {
  if (seconds == null) return undefined
  const div = DURATION_DIV[durationUnit.value] ?? 1
  return seconds / div
}

/**
 * 时长改数字。写回的是秒。
 * @param amount 当前单位下的数字。清空按 0。
 */
function onDurationAmount(amount: number | null) {
  const div = DURATION_DIV[durationUnit.value] ?? 1
  durationFromInput = true
  emit('update:modelValue', Math.round(Number(amount ?? 0) * div))
}

/**
 * 换时长单位。不改已存的秒。
 * @param unit 下拉值。
 */
function onDurationUnit(unit: string | number | (string | number)[] | undefined) {
  if (typeof unit !== 'string' || !(unit in DURATION_DIV)) return
  durationUnit.value = unit
}

/**
 * 日期。清空写成空串，单日以外的值忽略。
 * @param value 日期控件的值。
 */
function onDate(value: string | [string, string] | undefined) {
  if (Array.isArray(value)) return
  emit('update:modelValue', value ?? '')
}
</script>

<template>
  <div v-if="isByte" class="flex gap-2">
    <ENumberField
      class="flex-1"
      :model-value="byteAmount"
      :min="byteBound(spec.min)"
      :max="byteBound(spec.max)"
      :precision="spec.precision ?? 2"
      @update:model-value="onByteAmount"
    />
    <ESelect
      class="w-28"
      :model-value="activeUnit"
      :options="spec.unitOptions ?? []"
      @update:model-value="onUnit"
    />
  </div>
  <!-- step 默认 1。min=0.01 时合法值会变成 0.01、1.01，0.8 会被吸走。 -->
  <ENumberField
    v-else-if="spec.kind === 'int' || spec.kind === 'float'"
    :model-value="typeof modelValue === 'number' ? modelValue : undefined"
    :min="spec.min ?? undefined"
    :max="spec.max ?? undefined"
    :step="spec.kind === 'float' ? 0.01 : 1"
    :precision="spec.kind === 'float' ? 2 : 0"
    @update:model-value="emit('update:modelValue', $event)"
  />
  <div v-else-if="spec.kind === 'duration'" class="flex gap-2">
    <ENumberField
      class="flex-1"
      :model-value="durationAmount"
      :min="durationBound(spec.min)"
      :max="durationBound(spec.max)"
      :precision="durationUnit === '秒' ? 0 : 2"
      :step="durationUnit === '秒' ? 1 : 0.01"
      @update:model-value="onDurationAmount"
    />
    <ESelect
      class="w-28"
      :model-value="durationUnit"
      :options="DURATION_OPTIONS"
      @update:model-value="onDurationUnit"
    />
  </div>
  <EDatePicker
    v-else-if="spec.kind === 'date'"
    class="w-auto"
    :model-value="typeof modelValue === 'string' && modelValue ? modelValue : undefined"
    :clearable="!spec.required"
    @change="onDate"
  />
  <ESwitch
    v-else-if="spec.kind === 'bool'"
    :model-value="Boolean(modelValue)"
    @update:model-value="emit('update:modelValue', $event)"
  />
  <ESelect
    v-else-if="spec.kind === 'enum'"
    :model-value="String(modelValue ?? '')"
    :options="spec.options ?? []"
    @update:model-value="onEnum"
  />
  <EInput
    v-else
    :model-value="String(modelValue ?? '')"
    :maxlength="spec.maxLength ?? undefined"
    @update:model-value="onText"
  />
</template>
