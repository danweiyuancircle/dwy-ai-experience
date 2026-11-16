# 项目内 Flutter 工具链安装方案

> 历史安装提案。当前已按用户要求升级到 Flutter 3.50.0；正式基线见 `flutter/docs/development-baseline.md`，验证见 `flutter/docs/flutter-3.50-migration.md`。下文旧版本和未安装状态不再代表当前环境。

本文件保留先前项目内安装建议，**未执行，现已被用户要求复用现有 SDK 替代**。当前使用 shell 配置中已有的 Flutter 3.47.9 / Dart 3.13.7；本机路径只记录于本地任务日志，不成为源码依赖。以下 clone 步骤不再执行。

## 已核实来源与版本

- 工具：Flutter 官方 SDK 3.47.9 stable，包含 Dart SDK；发布方 Flutter team，BSD-3-Clause。
- 官方源仓库：https://github.com/flutter/flutter
- 版本来源：https://github.com/flutter/flutter/releases/tag/3.47.9 ，官方页面显示 2026-10-29 标记，已超过 7 天。
- `git ls-remote --tags https://github.com/flutter/flutter.git 3.47.9` 回读提交为 `c197ca5199e9ee5661e865596c9c07294dfab51c`；下载后再核对相同提交。
- 新发布的 3.50 不作为这次未经验证的自动升级目标。当前包最高最低要求为 Dart 3.12 / Flutter 3.44；3.47.9 仍需通过真实解析确认所有插件和生成器兼容。

## 范围

- 位置：共享仓库根的 `.build/toolchains/flutter-3.47.9/`，不加入全局 PATH，不替换其他 SDK。
- 使用当前已安装的 Xcode 和 Android SDK，不全局切换 xcode-select，不自动接受 Xcode/Android 许可，不安装模拟器镜像。
- 不自动安装或连接官方插件/MCP；本轮使用已读取官方 Skills 与官方 CLI。MCP 连接和额外权限另行确认。
- 获取 SDK 的 Git 源码和其初始化所需 Dart/引擎构建产物；依赖解析下载已批准库及其传递依赖，记录完整锁文件。
- SDK、依赖缓存和构建会写入本地工具目录、pub/Gradle 等标准缓存并占用磁盘；首次运行可能下载原生产物并执行已解析依赖的构建钩子。下载来源与失败信息需记录，不运行不明来源远程脚本。
- 不上传业务源码、手机内容或凭据。SDK 工具可能有遥测设置，首次运行前核对该版本的关闭方式；需要写工具设置时只关闭遥测，不更改其他全局偏好。

## 拟执行步骤

从仓库根执行：

```bash
git clone --depth 1 --branch 3.47.9 https://github.com/flutter/flutter.git .build/toolchains/flutter-3.47.9
git -C .build/toolchains/flutter-3.47.9 rev-parse HEAD
.build/toolchains/flutter-3.47.9/bin/flutter --version
.build/toolchains/flutter-3.47.9/bin/flutter doctor -v
```

核对源码提交、工具行为及版本后，用项目内 CLI 完成 `flutter pub get`、数据库代码生成、格式化、analyze、Dart/Widget 测试与构建；官方 CLI 生成移动宿主后设置 iOS 18 / Android minSdk29。访问本机 Playground 使用 `http://127.0.0.1:5188/`，实际运行后才报告可访问。

以上是具体范围，不是安装已完成的证据。网络不可达、解析冲突、SDK 与 Xcode/插件不兼容时先记录并修复授权范围内问题，不静默换 SDK、升级依赖或清空数据。

## 为什么需要确认

团队 `dwy-tool-discovery` 明确要求：官方与非官方工具都须先说明具体方案，再确认安装。当前环境未找到 Flutter/Dart SDK，因此代码开发授权还不能代替本次工具安装方案的确认。源码、配置与规范工作可以继续，SDK 依赖的运行验证须等待明确答复。
