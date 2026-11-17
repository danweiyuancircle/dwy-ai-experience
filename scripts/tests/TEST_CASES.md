# 发布回归

执行：`python3 -m unittest discover -s scripts/tests -p 'test_private_release.py'`。

| 测试 | 保护行为 |
| --- | --- |
| npm 工作区与独立包 | 根工作区禁止上传，独立包允许公开发布 |
| OIDC 发布入口 | npm/PyPI 使用短期身份，不使用长期发布 token |
| GitHub 仓库访问 | 接受公开和私有仓库；无效响应、网络错误或无效仓库名时中止 |
| webhooks 集成 | 共享 CI 覆盖包测试、构建及依赖配置 |
| 完整性 | 修改真实产物字节后校验失败 |
| 外部文件清单 | 拒绝目录逃逸、未列出的包、无效标签和源提交 |
| 产物目录 | 拒绝空目录和环境文件 |

外部 GitHub 查询使用固定响应替身；摘要、文件与清单验证使用真实临时目录。真实仓库访问和发包下载由发布工作流及发布后的安装 smoke 验证。

## Apple 云端环境

`.github/workflows/private-release.yml` 的 Apple 作业在 macOS 26 / Xcode 26.0.1 与 macOS 27 / Xcode 27.2 两组 ARM64 环境运行。macOS 27 使用 GitHub 官方 `xcode-27` 公开预览标签，见 [runner 标签](https://github.com/actions/runner-images/blob/main/README.md) 与 [镜像工具链](https://github.com/actions/runner-images/blob/main/images/macos/xcode-27-arm64-Readme.md)。

两组执行相同的 Swift 单测、模板生成回归、macOS arm64 与 iOS 模拟器 SDK 编译；最低部署目标继续为 macOS 26 / iOS 18。`fail-fast: false` 保留两组独立结果，联合打包通过 `needs: [apple, device]` 等待两组 Apple 作业和设备指纹作业均成功。作业输出实际系统、架构及工具链版本，不将 YAML 校验或本地测试当作云端运行成功。
