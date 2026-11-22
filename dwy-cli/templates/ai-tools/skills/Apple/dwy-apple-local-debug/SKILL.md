---
name: dwy-apple-local-debug
description: 用户要求在本机打包、更新、安装或启动 macOS Debug 应用，或在 iOS 模拟器上安装、更新或启动 Debug 应用时使用。普通编译、自动化测试、真机调试和商店归档沿用项目对应入口。
---

# Apple 本地调试

- **iOS 模拟器**：按 [iOS QA 调试流程](references/ios-simulator.md) 选择系统，用 [QA 设备脚本](scripts/ios_qa_device.py) 查找或创建设备，然后构建、安装和启动。
- **macOS 应用**：按下方流程构建、安装和启动本机 Debug 应用。

## macOS 本地 Debug 打包

从当前仓库和本机安装读取本轮的参数，直接调用随 Skill 分发的 [构建安装脚本](scripts/build_debug.py)。参数只传给本轮命令，每次按当前上下文重新核对。

### 读取本轮参数

1. **工程与产物。** 先读项目约定、工程生成配置、已有构建脚本和 Xcode scheme。需要消除歧义时，用 `xcodebuild -list` 或限定工程、scheme、Debug 和 macOS 目标的 `-showBuildSettings`，只提取应用 target 的 `PRODUCT_BUNDLE_IDENTIFIER`、`FULL_PRODUCT_NAME`、`TARGET_BUILD_DIR`、`DEVELOPMENT_TEAM` 和签名权限路径。沿用项目的架构、工具链、依赖锁定参数和独立的固定 Debug 构建目录。将本次构建生成的临时包传给 `--product`，脚本会在安装启动成功后清理它。把工程生成等前置步骤放在共享脚本锁内的构建命令里。构建号写进包元数据。
2. **安装与签名。** 核对当前进程、已安装包的 Bundle ID、团队和签名权限。安装位置为 `~/Applications/<名称>.app`。已有唯一用户级安装时沿用其文件名作为 `--app`，首次安装则使用实际产物名称。脚本要求 Apple Development 签名与 Debug 的 `com.apple.security.get-task-allow` 权利。发现其他运行实例、正式安装冲突或历史重复副本时，先核对来源和数据保护范围。
3. **数据。** 从实际沙盒签名权限、App Group、偏好域以及应用持久化代码定位数据路径，与本机目录核对。用可重复的 `--data` 传入实际数据目录或偏好 plist。SQLite 传入所在目录以保留 WAL。确认没有持久化用户数据时才使用 `--stateless`。有多个可行目标，或仍无法确定签名、安装或数据范围时，只询问无法核实的项。

### 执行

```bash
/usr/bin/python3 "$SKILL_DIR/scripts/build_debug.py" \
  --app 'Example.app' --bundle-id com.example.app --team-id YOURTEAMID \
  --product "$PWD/build/Debug/Build/Products/Debug/Example.app" \
  --data "$HOME/Library/Containers/com.example.app" -- \
  xcodebuild -project Example.xcodeproj -scheme Example -configuration Debug \
  -destination 'platform=macOS' -derivedDataPath "$PWD/build/Debug" build
```

`SKILL_DIR` 是当前已同步的 Skill 根目录。用前面核实的本机参数填充命令，在项目规定的目录执行。备份由共享脚本按 Bundle ID 保存在用户 Library 下的 DWY Debug Build 目录。

### 安装验证

脚本正常退出旧实例，验签新包，对照备份与源文件并检查 SQLite 完整性，在固定路径原子替换，再核对启动路径和唯一实例。构建、身份或数据校验失败时保留原安装；启动确认失败时尝试换回原包。回滚只涉及应用包，数据变更需按项目流程检查备份，确认后再恢复。

交付时报告实际安装路径、构建与启动结果。需要验收设备档案、登录或 GUI 时，从实际运行的应用验证。
