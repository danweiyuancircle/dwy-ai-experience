# 2.x 内部 breaking

2.x 的 minor / beta 也可以不兼容。整条线仍用 `v2/`，破坏点记在这里。细节 clone `@dwydev/eui@x.y.z`，不要另开 `v2.4/` 目录。

完整段落以该 tag 的 `frontend/eui/CHANGELOG.md` 为准。

| 版本 | 破坏点 |
|------|--------|
| 2.4.0 | 正式线。删除 `EAIChat`、`ETimetableGrid`、`EDataPage`、`EVirtualTable`、`EInputOTP`、`EChartContainer`、`useToast`。OTP 用 `EPinInput` + `otp`；虚拟表用 `ETable virtual`；轻提示用 `useMessage`。`ETable` 不用 `w-max`，列宽之和写入 `minWidth` |
| 2.4.0-beta.8 | 上表删除在 beta 线落地；停在 beta.1–7 的项目按此行 |
| 2.4.0-beta.9 | `ETable` 去掉 `w-max`，长单元格不再把末列撑出视口 |
| 2.4.0-beta.4 | 曾把表改成 `w-max` 以支持窄屏横滑；被 beta.9 / 2.4.0 修正 |

2.3.0 仍有上表删除前的组件。从 2.3 升 2.4 先全仓搜这些符号。仍停在 2.4.0-beta.N 的项目对照上表对应行，不要用 2.4.0 正式线冒充。
