# dwy-device-fingerprint

## 0.1.0

- 首次通过 GitHub Actions OIDC 发布到公开 PyPI，导入命名空间为 `dwy_device`。
- 仅使用 Python 标准库采集 Windows、macOS、Linux 系统身份，按应用作用域派生设备指纹，并返回明确的可用性、来源和错误状态。
- 支持 Python 3.9+，不依赖 EAPI、FastAPI 或业务包；可独立安装，或通过 `dwyeapi[device]==0.12.0` 使用 EAPI 门面。

