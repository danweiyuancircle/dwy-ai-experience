# 弹层

- 显隐统一 `v-model:open`，不要 `:visible` / `@update:visible`。
- `EDialog` body 有 `overflow-y-auto`，首尾表单控件的 focus-ring 会被裁。内容区加 `p-1` / `py-1`。
- `ESheet` 与 `EDrawer` 场景不同：Sheet 侧向覆盖（手机导航），Drawer 底部抓手。不要合成一个组件。
- `EAlertDialog` / `EConfirmDialog` / `useMessageBox` 场景不同，不要互相替换当「唯一确认框」。
