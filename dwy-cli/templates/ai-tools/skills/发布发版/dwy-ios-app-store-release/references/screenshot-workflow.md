# iOS/macOS 截图工作流

尺寸、格式、张数与 canonical 画布只以 [screenshot-specs.yaml](screenshot-specs.yaml) 为准。后续自动 P 图也读那份文件。

## 是否更新

- `source=first`：必须采集并上传，`screenshots.update=true`
- 后续版本默认 `screenshots.update=false`：把现网各 `displayType` 截图拷到本版本，不问
- 仅当本版功能变化很大（新主界面、新核心能力、旧截图已不能代表产品）时，才确认是否改为 `true`
- `true`：按规格处理后再传，旧图不留在本版本对应语言/尺寸槽

## 采集

从真实 iOS 模拟器和 macOS 应用构建采集截图。先向用户确认截图剧本：启动方式、测试账号引用、页面路径、测试数据、脱敏规则和中英文文案。禁止以与实际应用不一致的生成图替代功能展示。

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
