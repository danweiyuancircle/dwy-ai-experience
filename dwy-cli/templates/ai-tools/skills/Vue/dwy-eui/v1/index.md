# @dwydev/eui 1.x

1.x 没有 `v2/` 那套删减。精确 API clone `@dwydev/eui@1.y.z` 或读该版本 `node_modules`。

- **没有** `component-manifest.json`（2.1.0 才有）。`ls node_modules/@dwydev/eui/dist/components/` 定位目录。
- 轻提示可能是 `useToast`，不是 `useMessage`。
- 可能仍有 `EInputOTP`、`EVirtualTable`、`EDataPage`、`EAIChat` 等；不要按 2.4 清单当成已删除。
- 升 2.4 前读 `v2/breaking.md`，全仓替换已删符号。
