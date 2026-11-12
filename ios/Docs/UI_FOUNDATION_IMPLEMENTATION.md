# Apple UI 首批组件实现与验证

日期：2026-11-12。状态：源码可本地消费；尚未发布、迁移 ADBox 或完成 macOS 26 目标系统验收。总方案见 `ios/Docs/UI_FOUNDATION_PLAN.md`。

## 产品与实现

| 范围 | iOS 18+ | macOS 26+ Apple Silicon |
|---|---|---|
| 产品 | DesignKitIOS | DesignKitMac |
| 源码 | `ios/Sources/iOS/DesignKit/` | `ios/Sources/macOS/DesignKit/` |
| 主题 | EControlTheme、EAccentColors | EControlTheme、ESemanticColors、ETypography、ESpacing |
| 操作 | EButton、EIconAction、EMenu、EActionGroup | EButton、EIconAction、EMenu、EActionGroup |
| 选择 | EPicker（menu/segmented）、ESwitch | EPicker（menu/segmented）、ESwitch、ECheckbox |
| 输入 | ETextField、ESecureField、ESearchField、EField、EForm | ETextField、ESecureField、ESearchField、EField、EForm、EComboBox |
| 内容 | ECard、ESettingsRow、ELabelValue、EStatusBadge、EStateView | ECard、ESettingsRow、ELabelValue、EStatusBadge、EContentState |
| 反馈 | ENotice、ENoticeCenter、ENoticeHost、EInlineNotice、EProgressValue、ETaskProgress | ENotice、EToastMessage、EToast、EProgressFraction、ETaskProgress |
| 独立示例 | `ios/Examples/IOSControls/` | `ios/Examples/MacControls/` |

两端只共享已有 DesignCore 语义，不互相依赖；不引用 ADBox。未新增运行时依赖。已有 ThemeManager 与持久化键保持原样，控件主题只承载值，业务服务和任务不进入 Environment 默认值。

### E 前缀命名

首批未发布 API 统一使用 E 前缀，主题修饰器使用 `eControlTheme` / `eControlPlacement`。平台由所导入的模块区分：iOS 导入 DesignKitIOS，Mac 导入 DesignKitMac；同名 EButton 仍是两端各自实现，不表示已经共享了控件源码。跨平台应用按平台选择 import，需要同时导入时使用模块限定名，例如 `DesignKitMac.EButton`。

这次直接替换未发布的旧前缀，不保留旧名称别名。组件源文件、示例、测试及本文档同步采用新名称；产品名、target、平台目录和既有 ThemeManager 不改名。

默认品牌、语义字体与间距来自 `ios/Docs/DESIGN_TOKENS.md`。每个独立 scene/窗口装配本端主题；产品通过品牌配置统一覆盖，资源通过 Text/Label 等原生入口传入。危险角色不随品牌覆盖。

原生按钮负责 pressed/keyboard/disabled；busy 保留名称并阻止重复动作。iOS 浮动操作在 26+ 使用原生玻璃，18 保留标准样式。内容卡片不默认玻璃化。Menu 内继续使用系统 Button/Toggle/Section，不另造菜单模型。

EComboBox 改用原生 NSComboBox，关闭自动补全，明确激活提交与失焦通知分开；候选去重、过滤和重排保持文本身份。原生弹层替代旧 overlay，完整键盘与 IME 行为仍需目标系统验收，不能沿用旧原型的行为结论。

两端提示均处理消息替换、取消、焦点/交互停留与动态 VoiceOver。非关键成功可计时消失，重要错误持久显示。公告采用宿主 locale 并保留调用方资源 bundle。两端 API 保留各自生命周期模型，不强行合并为共享状态机。

## 独立接入

iOS 完整入口见 `ios/Examples/IOSControls/IOSControlsApp.swift`；包含本地化资源、标准/品牌主题、原生导航、表单、状态和提示宿主。Mac 完整入口见 `ios/Examples/MacControls/Sources/MacControlsGallery/MacControlsGallery.swift`。

这些示例只依赖对应公开产品。示例的仓内相对路径用于验证当前未发布源码，不是业务工程应提交的依赖方式。

```sh
# 仓库根：Mac 定向与完整回归
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --filter DesignKitMacTests
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift run MacControlsGallery
python3 -m unittest discover -s ios/Tests -p 'test_*.py'

# iOS 展示目录内生成，然后在 Xcode 选择实际目标模拟器运行或测试
cd ios/Examples/IOSControls
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodegen generate
```

导航、确认、sheet、分享/文件选择继续遵守原生实际触发源与窗口所有权规则；本轮没有新增完整呈现框架、页头或检查器 API。设备卡、日志表、付费展示等领域模块仍按总方案准入，未加入基础设计产品。

## 本轮验证

| 检查 | 结果与边界 |
|---|---|
| 根 SwiftPM 完整测试 | 本机 macOS 27.2.1：216 项通过，其中 Mac 组件 14 项；iOS 条件测试在 Mac 不计入覆盖 |
| Mac 组件定向测试 | 14 项通过：默认主题/四种外观对比、长文案/字号、进度边界、原生 Combo 配置与回调/候选/组合文本、提示生命周期与 locale/bundle |
| iOS 独立工程 | Swift 6 包编译和签名测试构建通过，只链接 DesignKitIOS；未以独立 typecheck 替代工程构建 |
| iOS 18.6 | 12 项单元测试、3 项 XCUITest 通过 |
| iOS 26.5 | 同一组 12+3 项通过 |
| iOS 27.0 | 同一组 12+3 项通过 |
| iOS 实际操作 | 原生键盘输入保留原文并更新绑定；分段双向选择；主按钮左右边缘各触发一次 |
| iOS 单元边界 | 375/393/430 pt 与辅助字号布局、进度拒绝非法数据、主题、提示替换/取消/释放/停留/VoiceOver、资源与公告语言 |
| 视觉核对 | iOS 27 默认中文页面截图核对；Mac 27 窗口默认蓝/危险/忙碌显示和原生 combo 可访问树初步核对，不代表完整矩阵 |
| 模板 | 3 项真实生成测试通过；iOS 18 / Mac 26 arm64，两套依赖图均精确锁定现有已发布版本 |
| Mac 展示产物 | arm64、Mach-O minos 26.0、Info.plist 最低 26.0；ad-hoc 签名验证通过，只保留固定展示 app 路径 |
| CI | Apple runner 改 macos-26，Mac 只构建 arm64、iOS 18 显式构建平台库，避免编译 Mac 示例；未触发远端 Actions |

本轮 Xcode 与 SwiftPM 两套依赖图核对了 pins 的新增、删除和改变，均无版本/revision变化。失效本地 GRDB 镜像仅通过命令级 URL 映射复用已核对标签与提交的缓存；本机路径不写入模板或提交锁文件，验证引起的锁文件 identity 污染已恢复。

本地证据（忽略的构建目录，不作为稳定下载地址）：iOS 工程结果位于 `.build/ios-controls/Logs/Test/`，截图 `.build/ios-controls-evidence27.png`；Mac 展示包 `.build/mac-controls-gallery/MacControlsGallery.app`。

### E 命名调整复验

同日按用户要求，将首批组件及主题的 IOS/Mac 前缀替换为 E，环境及修饰器改为小写 e 前缀；源码文件、测试、示例和规范同步更新。此次为未发布 API 的命名调整，不改变布局、事件、业务或平台基线。工作基于既有未提交实现，HEAD 为 `51a27a0e95a471ab626324ea6a314185f3cea6b9`，未改动已有其他任务内容。

- 根 SwiftPM 全量 216 项通过，包含 Mac 组件 14 项；独立 Mac 展示构建及更新后固定 app 的签名验证通过。
- iOS 独立工程测试构建通过；iOS 18.6、27.0 各 12 项单元测试与 3 项 XCUITest 通过。26.5 的结果属于改名前首批实现，此次纯命名调整未重跑该节点。
- 检查源码与调用处，旧组件前缀及旧修饰器无残留；保留平台 product/target/目录与测试类名。双端同名类型由模块限定，不新增共享控件实现或兼容别名。
- 独立只读命名审查未发现阻断：系统 macOS 条件、既有业务来源引用及 ThemeManager 保持原义，未发现消费文件同时导入两端 UI 模块。
- `git diff --check` 通过；依赖 pins 新增、删除、改变均为空，恢复验证导致的本地镜像 identity 污染。iOS 测试完成后模拟器均关闭。
- 本次未重新进行视觉、输入法或 macOS 26 现场验收；下列发布前门槛继续有效。

## 发布前剩余门槛

- 当前没有可用 macOS 26 实机环境；本机 27 的构建/测试/窗口不代替 26 验收。
- Mac GUI 工具在读取窗口与下拉后，后续动作返回 `noWindowsAvailable`；未确认鼠标选择提交、循环导航、Esc 原文、IME 和屏幕边缘行为通过。不能用离屏 AXUnknown 推断产品角色错误，也不能靠手动设置 AXRole 伪造通过。
- VoiceOver 实际朗读顺序、输入法组合、AutoFill、减少透明度/动态效果、高对比、iPad 呈现与完整窄窗/独立窗口仍需现场验收；纯状态和布局测试不代替这些检查。
- 模板仍依赖已发布 0.4.1，未调用本轮新 API。组件发布后同步两套精确版本和默认接入示例，再验证远端消费；不能把本地示例通过解释为旧标签已提供新 API。
- ADBox 依赖边界与逐页迁移、领域组件抽取、稳定版本发布属于总方案后续阶段，尚未执行。本轮未提交、推送、发布或更新已安装 Skills。
