# iOS/macOS 截图工作流

尺寸、格式、张数与 canonical 画布只以 [screenshot-specs.yaml](screenshot-specs.yaml) 为准。后续自动 P 图也读那份文件。

## 是否更新

- `source=first`：必须采集并上传，`screenshots.update=true`
- 后续版本默认 `screenshots.update=false`：把现网各 `displayType` 截图拷到本版本，不问
- 仅当本版功能变化很大（新主界面、新核心能力、旧截图已不能代表产品、What's New 写了的能力在现网截图里看不到）时，才确认是否改为 `true`
- `true`：按规格处理后再传，旧图不留在本版本对应语言/尺寸槽

## 采集

从真实 iOS 模拟器和 macOS 应用构建采集。先向用户确认截图剧本：启动方式、测试账号引用、页面路径、测试数据、脱敏规则和中英文文案。禁止以与实际应用不一致的生成图替代功能展示。

- 模拟器外观跟系统，与 App 主题无关。深色产品先 `xcrun simctl ui <udid> appearance dark` 再 launch。
- 画布必须落在目标 display 的 accepted 像素。真机分辨率不等于商店槽（如 6.1" 机 1170×2532，6.5" 槽要 1242×2688）。用该槽原生机型模拟器，或缩放且无 1 像素误差。
- 状态栏可用 `xcrun simctl status_bar override` 固定时间与电量。
- 中英各截一套。禁止同一张图只改文案冒充另一语言。
- 真机无线调试通常没有截图 CLI；锁屏无法 launch。截不到改模拟器。
- 禁止把尚未上架版本的界面写进仍在售版本的截图槽（Guideline 2.3.3）。

## 分平台输出

- iOS 与 macOS 必须分别采集、设计和上传，不能把同一张图缩放后两用
- iPhone 默认只出 `processing.canonical.ios` 指向的 display，画布用该 display 的 `preferred`
- 应用支持 iPad：另出 `processing.canonical.ipados`
- macOS 默认 `processing.canonical.macos`。内购审核图走 `macos_iap_review`
- 张数、格式、Alpha、色彩空间用 `processing` 字段，不要另写一套

## P 图契约

后续自动 P 图必须：

1. 读 `screenshot-specs.yaml` 的 `processing` 与对应 `preferred`
2. 画布精确等于 `preferred` 宽高，不留 1 像素误差
3. 去 Alpha、转 sRGB、导出 png 或 jpeg
4. 中英文各一套；iOS 与 macOS 分套
5. 先出本地预览清单，用户确认后再上传

## 上传前检查

检查尺寸是否落在该 display 的 accepted 列表、方向、格式、无透明通道、语言目录、页面顺序、隐私脱敏和平台归属。先生成本地预览和上传清单，用户确认后才上传。

## 只补现网已有槽

现网各 locale 的 `appScreenshotSets.screenshotDisplayType` 是槽位真相源。只向已有 displayType 补图或替换。不要因为 yaml `processing.canonical` 指向更大尺寸，就新建现网没有的 set。现网只有 6.5" 就出 6.5"；有 6.9" 才出 6.9"。

## 送审后锁死

`WAITING_FOR_REVIEW` / `IN_REVIEW` 不能增删改截图。API 409：`Can't Delete Screenshot After Submit for review` 或 `Can't Create Screenshot while Waiting For Review`。

同一版本里：截图、更新说明、描述、关键词已送审即锁；`promotionalText` 仍可 PATCH。

用户明确要求改已送审截图 → 先说明必须撤审、队列重排、定时发布日期可保留，再执行：

1. `PATCH /v1/reviewSubmissions/{id}` `{canceled: true}`
2. 等 submission `COMPLETE`、版本 `DEVELOPER_REJECTED`（不是 `PREPARE_FOR_SUBMISSION`）
3. 换图（见下「替换一张」）
4. **新建** `reviewSubmissions`（旧 id 作废）→ 挂同一 `appStoreVersion` → `submitted: true`
5. 核对 `releaseType` 与 `earliestReleaseDate` 仍在

## 替换一张（保留顺序）

`DELETE` 后再 `POST`，新图会排到该 set **末尾**。先记下原 index，等 `assetDeliveryState.state=COMPLETE` 后：

```
PATCH /v1/appScreenshotSets/{setId}/relationships/appScreenshots
{"data":[{"type":"appScreenshots","id":"<按原顺序的 id>"}]}
```

中英 set 分开替换，locale 不要混。
