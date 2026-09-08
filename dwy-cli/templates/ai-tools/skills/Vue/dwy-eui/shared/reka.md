# reka-ui 绑定

封装 reka-ui 原语时统一 `v-model`（`modelValue` / `update:modelValue`），**不是** `:checked` / `@update:checked`。

自己写包一层时用 `v-model` 或 writable computed。
