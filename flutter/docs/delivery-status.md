# Flutter 基础库交付状态

## 2026-11-16 · 前一版验证

下表记录迁移 Cupertino 之前的基础库与工具链验证。当前界面基线及旧代码归档见 `flutter/docs/design-system.md`。

| 项目 | 当前事实 |
| --- | --- |
| UI、图片与 Gallery | 23 项测试通过，详见 `flutter/docs/ui-3.50-validation.md` |
| 网络、日志、媒体、三类存储 | 50项测试通过；详见 `flutter/docs/foundation-3.50-validation.md` |
| 工作区 | 8个包和Playground统一解析成功，有真实lockfile；完整分析无诊断 |
| 数据库生成代码 | Dart3.14下实际执行build_runner生成成功 |
| Playground | Web构建通过；本轮未启动服务、未做浏览器视觉验收 |
| iOS / Android 宿主 | 未生成、未构建、未验收 |
| 开发规范 | 新库统一3.50/3.14基线；Flutter/stack发现同步回归7项通过 |

首次封装统一从Flutter3.50.0 stable / Dart3.14.0起步，不保留旧下限或旧UI兼容入口。精确基线见 `flutter/docs/development-baseline.md`；历史交接与安装提案不代表当前状态。

## 2026-11-27 · Playground

| 项目 | 当前事实 |
| --- | --- |
| Playground | 文档式目录、详情、防漂移测试；Gallery 27 项测试通过；Web 构建后用 Playwright 在 1280x800 和 430x900 截图并检查 |
| iOS / macOS 宿主 | 已用 `flutter create --platforms=macos,ios .` 生成，iOS 目标 18.0；Xcode 不完整、未安装 CocoaPods，未构建、未运行 |
| Android 宿主 | 未生成；Android licenses 未接受 |

以下两项来自前一版待办，其中 Web 可视验收已完成，原生构建与设备验证仍待办。

## 前一版待办

1. 使用官方CLI生成Playground移动宿主，设置iOS18 / Android10支持基线，执行构建和目标系统验证。
2. 启动可交互Playground并检查主题、品牌、基础组件、图片和关键失败路径，提供实际访问地址与运行证据。

本次记录时源码没有提交、推送或发布；包内已记录的上游限制需要在集成审查中逐项裁决，不能默认视为已接受的最终限制。
