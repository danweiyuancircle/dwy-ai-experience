# @dwydev/eui

Vue 3 组件库，基于 Reka UI、Tailwind CSS 4 和 vee-validate。应用根节点必须配置 `EConfigProvider`；样式接入见仓库 `docs/eui-integration-guide.md`。

## 日期选择器国际化

`EDatePicker` 默认占位为「请选择日期」，区间为「开始日期 至 结束日期」。在 `EConfigProvider.locale` 中局部覆盖 `datePickerPlaceholder`、`datePickerStartPlaceholder`、`datePickerEndPlaceholder`、`datePickerRangeSeparator` 即可统一文案，运行期切换立即生效。单日、月、年模式共用 `datePickerPlaceholder`。

```vue
<EConfigProvider :locale="{
  name: 'en-US',
  datePickerPlaceholder: 'Pick a date',
  datePickerStartPlaceholder: 'Start date',
  datePickerEndPlaceholder: 'End date',
  datePickerRangeSeparator: 'to',
}">
  <EDatePicker />
  <EDatePicker type="daterange" />
</EConfigProvider>
```

`locale.name` 仅控制日历月份、星期等日期格式，不自动翻译文案。组件显式传入的 `placeholder`、`startPlaceholder`、`endPlaceholder`、`rangeSeparator` 优先于全局配置，包括空字符串；分隔符同时用于占位和已选区间。

## 表单对话框（≥2.7.0）

给 `EForm` 设置页面内唯一 `id`，用 `EFormDialog` 的 `form` 关联。默认确认按钮通过原生 `submit` 进入 `EForm` 校验，业务只处理 `EForm` 的 `@submit`。`id` 是透传至原生 `<form>` 的属性，不是新增的 `EForm` prop。

以下组件由调用方传入异步 `save` 函数；成功后关闭，失败保留输入。`loading` 由业务维护，提交函数仍需防重入，以覆盖键盘或程序触发表单提交。

```vue
<script setup lang="ts">
import { computed, reactive, ref, useId } from 'vue'
import { z } from 'zod'
import { EAlert, EButton, EForm, EFormDialog, EFormItem, EInput } from '@dwydev/eui'

/** 保存回调由业务提供；请求失败应 reject，组件保留表单并展示错误。 */
const props = defineProps<{ save: (values: Record<string, unknown>) => Promise<void> }>()
const open = ref(false)
const loading = ref(false)
const error = ref('')
// 同一页面可挂载多个实例，关联 id 必须唯一。
const formId = useId()
const model = reactive({ name: '' })
const rules = z.object({ name: z.string().trim().min(1, '请输入名称').max(64, '最多 64 个字符') })
const confirmDisabled = computed(() => model.name.trim().length === 0)

/** EForm 仅在校验通过后触发；按钮禁用不能替代业务提交防重入。 */
async function handleSubmit(values: Record<string, unknown>) {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await props.save(values)
    open.value = false
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : '保存失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <EButton @click="open = true">编辑</EButton>
  <EFormDialog
    v-model:open="open"
    title="编辑名称"
    description="保存后立即生效"
    :form="formId"
    :loading="loading"
    :confirm-disabled="confirmDisabled"
    confirm-text="保存"
  >
    <EAlert v-if="error" variant="destructive" :title="error" />
    <EForm :id="formId" :model="model" :rules="rules" @submit="handleSubmit">
      <EFormItem label="名称" prop="name" required>
        <EInput v-model="model.name" :maxlength="64" :disabled="loading" />
      </EFormItem>
    </EForm>
    <template #footer-leading>
      <EButton type="button" variant="ghost" :disabled="loading" @click="model.name = ''">
        清空
      </EButton>
    </template>
  </EFormDialog>
</template>
```

- `description`：提供对话框说明与可访问描述。
- `confirmDisabled`：仅禁用默认确认按钮，取消与关闭仍可用；业务规则由调用方决定。
- `footer-leading`：在默认取消、确认按钮前追加操作。完整 `footer` 插槽仍会覆盖全部默认 footer，包括 `footer-leading`；自定义按钮的禁用、loading 和提交关联由调用方负责。
- `loading`：禁用默认确认、取消，并阻止 X、Esc、遮罩关闭；父组件仍可主动设置 `open=false`。
- 设置 `form` 后不派发 `confirm`，不要同时把保存函数绑定至 `@confirm`。不要用原生 `form.submit()` 绕过 submit 事件与校验；程序触发使用关联表单的 `requestSubmit()`。

### 兼容旧用法

不传 `form` 时，默认确认按钮保持 `type="button"` 并派发 `confirm`；已有 `@confirm` 处理函数可以继续手动调用 `EForm` 的 `validate()`。`loading` 或 `confirmDisabled` 为真时不会派发 `confirm`。迁移至原生表单关联时，将保存逻辑移至 `EForm @submit`，移除旧 `@confirm` 提交绑定。
