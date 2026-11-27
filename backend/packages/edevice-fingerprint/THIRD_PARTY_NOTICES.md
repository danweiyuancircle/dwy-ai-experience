# 开源参考

本模块参考下列 MIT 项目的系统身份来源及应用域隔离思路，使用 Python 标准库独立适配，不内嵌或安装上游包。

- [py-machineid](https://github.com/keygen-sh/py-machineid)：系统身份与应用专用 HMAC 思路，MIT。
- [machineid](https://github.com/denisbrodbeck/machineid)：Windows 64 位注册表视图、分平台采集与 ProtectedID，MIT。
- [node-machine-id](https://github.com/automation-stack/node-machine-id)：跨系统身份来源对照，MIT。

本模块固定自己的来源、规范化及 dwy.device.v1 派生协议，不宣称与上游输出兼容。项目发布范围遵守仓库私有分发约束。
