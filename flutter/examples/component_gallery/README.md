# DWY Component Playground

使用独立 Cupertino UI 和 DWY 主题，支持桌面侧栏与窄屏目录面板。图片页使用 `dwy_image` 公共 API；没有远程演示图片、默认 HTTP 请求或权限申请。

## 图片示例

- **Asset / Memory**：同一份仓库自制 PNG，展示 bundled asset 和不可变内存来源；不包含第三方素材。
- **外观与尺寸**：控制圆角与物理解码上限，不把解码尺寸误作服务端图片压缩。
- **失败与重试**：故意无效的内存图展示错误/重试，修复按钮切换为有效 PNG；网络首次失败端点用于实际重试恢复。
- **Network**：输入完整 HTTP(S) 地址后主动加载，不配置认证头，不把原始异常显示给用户。
- **Scope A / B**：同一地址使用不同命名空间。清理前先卸载当前图片，再等待 `clear()`；另一 scope 不清理。离开图片页后逐个清理并释放页面拥有的缓存，保留维护等待链。

`dwy_image` 的上游 Web 实现不具备与移动端相同的磁盘缓存。Web 可以验证外观与请求，不能证明移动端 scope 磁盘清理通过。缓存清理可能等待上游未结束的网络流；发起清理不等于完成。

## 可控本地图片服务

使用已批准并可用的 Dart SDK，在本目录运行：

```bash
dart run tool/image_fixture.dart
```

服务仅绑定 `127.0.0.1`，端口默认 `5189`（可传一个端口参数）。只读取仓库的 `assets/sample.png`，提供：

| 地址 | 行为 |
| --- | --- |
| `http://127.0.0.1:5189/image.png` | 正常图片 |
| `http://127.0.0.1:5189/slow.png` | 延迟1秒，用于观察占位 |
| `http://127.0.0.1:5189/flaky.png` | 首次请求503，之后成功，点击图片内重试验证 |
| `http://127.0.0.1:5189/missing.png` | 404，验证稳定错误展示 |

在图片页粘贴地址并点击加载。此地址用于同机浏览器/桌面；真机的 localhost 指手机自身，移动端请求需由集成验收配置设备可达的服务和系统网络策略，不扩大监听到公网。

## 官方 Widget Preview

最低目标为 Flutter 3.50 / Dart 3.14；精确开发版本见 `flutter/docs/development-baseline.md`。`lib/previews/image_previews.dart` 提供两个官方 `@Preview` 入口，分别显示浅/深主题的 memory 图片，不创建缓存管理器或调用原生 API。

```bash
flutter widget-preview start
```

注解导入 `package:flutter/widget_previews.dart`，没有引入额外 preview 包；首次运行仍由工作区集成验证 SDK API 与 Web 转译兼容性。

## 验证入口

使用工作区锁定的 Flutter 版本运行 `flutter test`，测试说明见 `test/TEST_CASES.md`。移动宿主集成可选同一条搜索、编辑、弹层、返回流程分别在 iOS 和 Android 验证。
