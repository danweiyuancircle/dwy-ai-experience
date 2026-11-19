# 表单

- **禁止原生 `<form>`**，一律 `<EForm>`。EForm 带 vee-validate、provide/inject、label 布局、`reset` / `validate`。
- `ESelect` 的 `option.value` **不能是 `''`**，reka-ui 不支持。筛选项用哨兵（如 `'all'`），请求时再转 `undefined`。
- 校验优先 zod schema 交给 `EForm` 的 `rules`。
- `useFormField` 只在 `EFormItem` 内有值；表单外返回 `null`，不要当 vee-validate `<FormField>` 用。

## 表单对话框（EUI ≥2.7.0）

- `EForm :id="formId"` 与 `EFormDialog :form="formId"` 配对；`formId` 在页面内唯一，可用 Vue `useId()`。`id` 透传到 `EForm` 根 `<form>`，不是新 prop。
- 保存函数只绑定 `EForm @submit`：默认确认按钮通过原生 submit 进入 vee-validate 校验，通过后才触发 `submit`。不要同时绑定 `EFormDialog @confirm` 保存；关联 `form` 时不派发 `confirm`。
- `confirm-disabled` 只禁用默认确认按钮；`description` 提供可访问说明；`#footer-leading` 在默认按钮前追加操作，追加按钮显式设 `type="button"`。
- `loading` 阻止默认取消、确认、X、Esc、遮罩关闭；父组件仍可 `open=false`。业务提交函数仍需检查 loading，覆盖键盘或程序提交防重入。
- `#footer` 整体覆盖默认 footer 与 `#footer-leading`，自定义按钮行为由调用方负责。
- 旧项目不传 `form` 时保留 `@confirm`，默认确认为普通按钮；可继续手动 `validate()`。迁移时改为 `EForm @submit` 单入口。
- 程序提交使用 `requestSubmit()`；原生 `form.submit()` 会绕过 submit 事件与校验。完整 Vue 示例见仓库 `frontend/eui/README.md`。
