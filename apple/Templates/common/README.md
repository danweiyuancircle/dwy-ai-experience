# __APP_NAME__

Apple 四层项目，当前外部基础库模板版本为 `__PACKAGE_VERSION__`。完整边界见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，修改约定见 [AGENTS.md](AGENTS.md)。

| 层 | 目录 / 依赖 |
| --- | --- |
| ① App | 已生成平台的 ios/App 或 macos/App |
| ② Features | 本端 Features 与 BusinessUI |
| ③ BizFoundation | packages/__APP_NAME__Core；按需本端 Platform |
| ④ Foundation | AppleAppKit 的实际 products |

只生成所选平台，不为未使用的平台或业务 UI 建空包。业务核心由各端引用同一份；已有组件满足需求直接用，BusinessUI 只放业务定制，不逐个包装基础控件。

## 首次运行

需要 Python 3、Swift 6、XcodeGen；SDK 编译和运行另需完整 Xcode。可用 DEVELOPER_DIR 为当前命令指定 Xcode，不必修改全局选择。

从产品根执行：

```bash
python3 scripts/check-architecture.py
swift test --package-path packages/__APP_NAME__Core
```

进入已生成的 ios 或 macos 目录，运行：

```bash
xcodegen generate
open __APP_NAME__.xcodeproj
```

配置开发团队、签名、正式商品与商店信息后，再按实际目标构建和运行。模板的产品 ID、隐私链接、反馈配置须在发布前核对。双端初建的 Bundle Identifier 使用所选前缀加 .ios / .macos；单端保留创建时传入的 ID。

iOS 从产品根另执行 `python3 -m unittest discover -s ios/Tests -p 'test_*.py'`。结构检查、单测不代替 SDK 编译、界面与实际业务验收。

## 增加另一平台

在基础库源码仓库执行 `apple/scripts/new-app.sh`，保留原产品名和输出父目录，增加 `--add-platform --platform ios` 或 `--add-platform --platform macos`，通过 `--bundle-id` 指定新端独立 ID。已有目标目录拒绝覆盖；业务核心、原平台及已有基础库版本保留，不重新生成。
