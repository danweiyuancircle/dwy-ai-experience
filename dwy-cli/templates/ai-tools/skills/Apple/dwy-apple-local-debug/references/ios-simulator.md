# iOS QA 模拟器调试

所有 iOS 项目共用同一 Mac 用户下的固定设备。

| 目标系统 | 设备名 |
| --- | --- |
| iOS 18 | `IOS18-QA` |
| iOS 26 | `IOS26-QA` |
| iOS 27 | `IOS27-QA` |

1. **选系统。** 优先使用用户指定的版本，其次用项目约定。日常安装调试未指定时，选项目支持且本机可用的最新 QA 大版本，只运行一台。系统回归沿用 `dwy-ios-development` 的覆盖规则，按改动范围增加目标。先确认项目的 deployment target 支持所选版本。
2. **选 Xcode。** 核对项目使用的 Xcode、SDK 和 runtime。`xcodebuild` 和 `xcrun simctl` 使用同一个 Xcode，可为本轮命令设置 `DEVELOPER_DIR`。保留全局 Xcode 设置。
3. **拿 UDID。** 调用 `scripts/ios_qa_device.py <大版本>`。只有名称与 iOS 大版本都匹配、设备可用时才复用，现有机型和系统小版本照用。缺设备时，脚本挑选对应大版本中有兼容机型的最新可用 runtime，优先使用标准版 iPhone 16，其次使用兼容的较新标准版 iPhone。缺 runtime、设备不可用或同名冲突时，报告具体问题并停止该目标。创建仅使用已安装的 runtime。
4. **构建、安装、启动。** 沿用项目既有的工程生成步骤、scheme、Debug 构建目录及依赖锁定参数。构建目的地固定为本轮查到的 UDID。用同一组构建参数核对应用 target 的 `TARGET_BUILD_DIR`、`FULL_PRODUCT_NAME` 和 `PRODUCT_BUNDLE_IDENTIFIER`，确认是本轮的模拟器 `.app`。核对已安装应用的 Bundle ID，使用 `simctl install` 就地更新，保留 App 数据及模拟器状态。遇到安装失败时保留原数据，避免以卸载、抹除、删除或重建作为重试手段。

以下示例使用 iOS 26。用实际工程及应用 target 参数填充命令。`SKILL_DIR` 取当前已同步 Skill 的根目录。

```bash
qa_udid="$(/usr/bin/python3 "$SKILL_DIR/scripts/ios_qa_device.py" 26)" &&
xcodebuild -project Example.xcodeproj -scheme Example -configuration Debug \
  -destination "platform=iOS Simulator,id=$qa_udid" -derivedDataPath "$PWD/build/Debug" build &&
xcrun simctl bootstatus "$qa_udid" -b &&
xcrun simctl install "$qa_udid" "$PWD/build/Debug/Build/Products/Debug-iphonesimulator/Example.app" &&
xcrun simctl launch --terminate-running-process "$qa_udid" com.example.app
```

交付时报告实际设备名、runtime 版本、复用或创建情况，以及安装和启动结果。需要验证界面或业务时，在该 UDID 对应的设备上实际操作，并单独记录结果。
