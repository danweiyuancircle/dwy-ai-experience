# ReorderableListExample

ID: designkit.mac.reorderable-list
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

排序交互由组件管理，顺序保存由宿主负责。

## 能力
- 原生拖拽排序 — 行通过系统排序手势移动。
- 可访问的移动 — moveUpLabel 和 moveDownLabel 为辅助功能操作命名。
- 调用方持久化 — onMove 决定是否接受移动，保存由调用方负责。
