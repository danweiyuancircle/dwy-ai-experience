---
name: dwy-apple-local-debug
description: 用户要求在本机打包、更新、安装或启动 macOS Debug 应用，或在 iOS 模拟器上安装、更新或启动 Debug 应用时使用。普通编译、自动化测试、真机调试和商店归档沿用项目对应入口。
---

# Apple 本地调试

- **iOS 模拟器**：按 [iOS QA 调试流程](references/ios-simulator.md) 选择系统，用 [QA 设备脚本](scripts/ios_qa_device.py) 查找或创建设备，然后构建、安装和启动。
- **macOS 应用**：按下方流程构建、安装和启动本机 Debug 应用。

## macOS 本地 Debug 打包

每次从当前工作区执行 Debug 构建，将最新结果原位安装并启动。本机只保留一个可搜索、可启动的同 Bundle ID 应用。直接调用随 Skill 分发的 [构建安装脚本](scripts/build_debug.py)，本轮参数从当前仓库和本机安装发现。

### 读取本轮参数

1. **工程与产物。** 先读项目约定、工程生成配置、已有构建脚本和 Xcode scheme。需要消除歧义时，用 `xcodebuild -list` 或限定工程、scheme、Debug 和 macOS 目标的 `-showBuildSettings`，只提取应用 target 的 `PRODUCT_BUNDLE_IDENTIFIER`、`FULL_PRODUCT_NAME`、`TARGET_BUILD_DIR`、`DEVELOPMENT_TEAM` 和签名权限路径。沿用项目的架构、工具链、依赖锁定参数和独立的固定 Debug 构建目录。将本次构建生成的临时包传给 `--product`，脚本会在安装启动成功后清理它。把工程生成等前置步骤放在共享脚本锁内的构建命令里。构建号写进包元数据。
2. **安装与签名。** 核对当前进程、已安装包的 Bundle ID、团队和签名权限。沿用 `/Applications` 或 `~/Applications` 中唯一现有的 Debug 安装，文件名传给 `--app`。首次安装使用实际产物名称，默认落到 `~/Applications`。脚本要求 Apple Development 签名与 Debug 的 `com.apple.security.get-task-allow` 权利。正式安装冲突时停止覆盖。

### 执行

```bash
/usr/bin/python3 "$SKILL_DIR/scripts/build_debug.py" \
  --app 'Example.app' --bundle-id com.example.app --team-id YOURTEAMID \
  --product "$PWD/build/Debug/Build/Products/Debug/Example.app" -- \
  xcodebuild -project Example.xcodeproj -scheme Example -configuration Debug \
  -destination 'platform=macOS' -derivedDataPath "$PWD/build/Debug" build
```

`SKILL_DIR` 是当前已同步的 Skill 根目录。在项目规定的目录执行。

### 安装验证

脚本构建并验签新包后退出旧实例，在固定路径原子替换应用包。安装只处理应用包，继续使用原有沙盒、App Group 和用户配置。构建或验签失败时沿用原安装。启动失败时用暂存的旧包恢复，启动成功立即清理暂存。

安装前后按 Bundle ID 核对 Spotlight 和 LaunchServices。构建产物在成功启动后注销并清理。发现历史副本时核对其来源，清理已确认可丢弃的 Debug 产物。保留正式归档和仍需要的回滚包时，将包放在 `.noindex` 目录并注销旧路径及残留注册，仅改扩展名仍可能被 Spotlight 搜到。完成后复查两处查询，唯一可发现的应用应为固定安装路径。项目带扩展时，同时核对扩展只注册在该安装包内。

交付时报告实际安装路径、构建与启动结果。需要验收设备档案、登录或 GUI 时，从实际运行的应用验证。
