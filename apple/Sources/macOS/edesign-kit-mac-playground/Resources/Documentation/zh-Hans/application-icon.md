# ApplicationIconExample

ID: designkit.mac.application-icon
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途

读取本机应用图标，缺失时显示指定符号。

## 能力
- 已安装应用图标 — 按 Bundle ID 通过 Launch Services 解析。
- 自定义路径 — appPath 覆盖尚未注册的应用。
- 回退符号 — 找不到应用时显示必填的 SF Symbol。
