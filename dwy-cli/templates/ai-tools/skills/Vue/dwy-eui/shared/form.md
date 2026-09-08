# 表单

- **禁止原生 `<form>`**，一律 `<EForm>`。EForm 带 vee-validate、provide/inject、label 布局、`reset` / `validate`。
- `ESelect` 的 `option.value` **不能是 `''`**，reka-ui 不支持。筛选项用哨兵（如 `'all'`），请求时再转 `undefined`。
- 校验优先 zod schema 交给 `EForm` 的 `rules`。
- `useFormField` 只在 `EFormItem` 内有值；表单外返回 `null`，不要当 vee-validate `<FormField>` 用。
