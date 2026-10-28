# dwy-device-fingerprint

## 0.1.1

- 首个公开 PyPI 版本, 通过 GitHub Actions OIDC 发布, 导入命名空间为 `dwy_device`。
- 修复 Windows 上执行 Linux 来源测试时的文本换行转换：夹具显式写入 Linux machine-id 的原始 LF 字节，保留主来源优先的完整断言与所有平台测试。
- 采集 API、指纹派生及原生系统来源保持不变；发布验收仅运行 Linux 与 macOS，不再运行 Windows runner。

## 0.1.0（未公开）

- 首次发布候选。Windows 测试夹具的换行断言未通过, 工作流在上传前停止; 保留该标签, PyPI 未上传此版本。
- 仅使用 Python 标准库采集 Windows、macOS、Linux 系统身份，按应用作用域派生设备指纹，并返回明确的可用性、来源和错误状态。
- 支持 Python 3.9+，不依赖 EAPI、FastAPI 或业务包；可独立安装，或通过 `dwyeapi[device]==0.12.0` 使用 EAPI 门面。
