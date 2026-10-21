# eapi 跨平台设备指纹模块方案

日期：2026-10-21。状态：轻量核心与 eapi 可选门面已实现，本地验证记录见对应实施计划；未发布版本。

目标：在 dwy-shared 的 eapi 体系内提供可复用设备指纹模块，结合 py-machineid 与其他开源实现中的原生采集方式，向 SDK、桌面 Python 进程及内部应用返回稳定的产品专用指纹和独立系统信息。目标是提高跨账号隐藏同一运行设备的成本，不承诺物理硬件唯一。

本模块不发送网络请求、不决定 HTTP 头、不记录设备信息日志，不处理额度、账号、公告或服务端管理页面。业务项目只调用公开 API，并决定如何缓存和上报结果。

## 1 现有结构与约束

eapi 发行名为 `dwyeapi`，当前源码位于 `backend/src/dwyeapi/`，包版本 0.11.1。`backend/pyproject.toml` 要求 Python >=3.11，并强依赖 FastAPI、SQLAlchemy、Pydantic、Redis 等。根导入还会加载配置、响应和日志模块。

QuantZone SDK 支持 Python >=3.9。仅增加 `dwyeapi.device` 并让 SDK 安装整个 eapi，会同时引入 Python 版本冲突和无关后端依赖；extras 不能移除发行包的基础依赖，也不能降低 requires-python。

仓库 `AGENTS.md` 的私有分发约束禁止新版本上传公共 npm/PyPI，当前通过 `.github/workflows/private-release.yml` 构建私有 Release。因此不能把新模块直接安排成公开 PyPI 依赖。

推荐“归属 eapi、核心可独立安装”：轻量核心放在 `backend/packages/device-fingerprint/`，eapi 提供可选门面。核心 Python >=3.9，仅标准库运行时依赖；现有 eapi 继续保持 Python >=3.11，不整体降级或拆除既有依赖。

## 2 开源参考与选型

以下三个项目均为 MIT，允许商用；实际适配或复制源码时保留对应版权和许可。三者是采集策略参考，不是同时安装的依赖。

| 项目 | 可以复用的思路 | 本模块不直接照搬的行为 |
| --- | --- | --- |
| [py-machineid](https://github.com/keygen-sh/py-machineid) | 三平台系统身份来源、应用专用 HMAC 派生 | shell 命令无 timeout；自动在系统、硬件和容器身份间回退；不返回来源 |
| [Go machineid](https://github.com/denisbrodbeck/machineid) | Windows 64 位注册表视图、分平台适配、ProtectedID | 不引入 Go 辅助程序或多语言打包 |
| [node-machine-id](https://github.com/automation-stack/node-machine-id) | macOS IOPlatformUUID、平台来源对照 | 不使用 hostname 回退，不采用无应用隔离的默认指纹 |

核验的 py-machineid 1.0.0 发布于 2025-12-02，MIT，发布时间超过七天。其实际 Windows 注册表读取依赖 winregistry，命令路径使用 shell=True 且没有超时参数；Linux 无 machine-id 时还会尝试 Docker 容器 ID。通过黑盒调用 `machineid.id()` 无法约束最终来源或统一超时。

源码依据：[py-machineid 采集与派生](https://github.com/keygen-sh/py-machineid/blob/master/machineid/__init__.py)、[Go 派生](https://github.com/denisbrodbeck/machineid/blob/master/id.go)、[Node 采集](https://github.com/automation-stack/node-machine-id/blob/master/index.js)。

### 2.1 三种实现路线

| 路线 | 内容 | 评价 |
| --- | --- | --- |
| 直接薄包装 py-machineid | 调用 id/hashed_id，补系统信息和返回类型 | 代码最少，但超时和身份来源不可控，不推荐作为共享模块默认实现 |
| 参考开源策略，使用标准库做原生适配 | 固定每个平台来源、校验与超时，复用成熟派生方式 | 推荐；无运行时小众依赖，行为明确，三平台范围可控 |
| py-machineid 与自研适配双链并行 | 原生失败后自动调用 py-machineid | 重复采集与来源漂移，维护两套逻辑，不采用 |

推荐将 py-machineid 作为参考实现，而不是运行时强依赖。基础模块只补标准库没有统一提供的跨平台适配，不实现硬件驱动、通用插件框架或复杂指纹评分。

## 3 原生身份采集

| 平台 | 固定主来源 | 实现方式 |
| --- | --- | --- |
| Windows | HKLM\\SOFTWARE\\Microsoft\\Cryptography 中的 MachineGuid | 标准库 winreg，显式选择 64 位注册表视图；不启动 PowerShell/WMIC |
| macOS | IOPlatformExpertDevice 的 IOPlatformUUID | 系统 ioreg 输出结构化 plist，标准库 subprocess 与 plistlib 处理 |
| Linux | /etc/machine-id，缺失时检查 /var/lib/dbus/machine-id | pathlib 有界读取，校验为非零的 32 位十六进制值 |

Windows/macOS UUID 做受控格式校验及大小写、分隔符规范化；Linux machine-id 校验长度、十六进制及全零值。两类来源都统一为规范化 32 位小写十六进制表示，再派生指纹。

Linux 优先使用 /etc/machine-id，仅当主文件不存在时尝试 D-Bus 路径；主文件存在但无权限或非法时返回明确错误，不通过另一来源掩盖问题。两个位置若在系统修复后变成不同值，属于底层身份变化，不承诺指纹不变。

macOS 使用固定可执行文件和参数数组，shell=False，默认命令超时建议 2 秒，超时可由调用者显式调整。限制命令查询深度与结果大小，不执行用户拼接命令。Windows 注册表读取和 Linux 文件读取均不需要提权。

系统工具、注册表和文件属于外部边界，必须处理缺失、权限、超时、无效值和受限大小；错误对象不携带原始身份或命令完整输出。

不自动切换到 MAC、hostname、随机 UUID、磁盘序列号、CIM 硬件 UUID或 Docker 容器 ID。稳定来源不可得时返回 unavailable。首期不创建安装 ID 文件，不依赖 platformdirs，也不维护隐藏副本。

容器、WSL、虚拟机只报告其当前系统环境提供的身份，不能据此判断物理宿主。克隆镜像可共享 ID，重装系统或管理员改系统 ID 可改变指纹。只有某次调用未获得身份时，不产生新的随机“设备”。

Linux 的原始 machine-id 不应直接传到网络，应用应使用产品专用派生值。[systemd 说明](https://www.freedesktop.org/software/systemd/man/latest/machine-id.html)

## 4 指纹派生与公开契约

公开入口建议为 `collect_device(namespace, *, command_timeout=2.0) -> DeviceInfo`。namespace 必填，由产品固定，例如 QuantZone SDK 与桌面 Worker 均使用 `quantzone`；不包含邮箱、Key、项目路径、venv 或 SDK 版本。

namespace 限制为 1 至 128 个 ASCII 字符，采用小写字母、数字、点、下划线与连字符，不进行隐式改写。超时必须为有限正数并限制上限。调用参数非法时抛 ValueError，采集失败则返回结构化结果。

算法固定为 HMAC-SHA256：key 使用规范化机器身份的 ASCII 字节；message 使用 `dwy.device.v1:` 与 namespace 拼接后的 UTF-8 字节。返回 64 位小写十六进制。此方式沿用开源应用隔离思路，并通过方案版本固定本库协议；不保证与 py-machineid.hashed_id 的原始输出相等。

相同系统身份、相同 namespace 和相同方案版本必须得到相同结果；不同 namespace 产生不同指纹。OS 版本、架构、来源标签、SDK 版本不参与哈希。

派生不是认证或防篡改机制。namespace 是公开产品域，不当作秘钥；客户端仍能伪造自报指纹。

### 4.1 返回类型

使用本库自己的不可变标准库 dataclass，不暴露上游类型，不依赖 Pydantic、FastAPI 或日志框架。

| 字段 | 含义与约束 |
| --- | --- |
| fingerprint | 成功时 64 位十六进制，失败时 None |
| scheme_version | 本库指纹协议版本，首期为 1 |
| source | windows_machine_guid、macos_platform_uuid、linux_machine_id、linux_dbus_machine_id；无来源时 None |
| status | available、unavailable、unsupported |
| error_code | None 或 unsupported_platform、not_found、permission_denied、timeout、invalid_value、command_failed |
| system | 独立 SystemInfo，不参与派生 |

SystemInfo 包含 `system_name`、`system_release`、`system_version`、`architecture`，分别对应标准库 platform 的同名语义，名称与架构最长 32 字符，版本最长 128 字符。系统元数据缺失可以为空，不改变已有指纹是否可用。Darwin/Linux 的 release 属于内核发行信息，不冒充 macOS 产品版本或 Linux 发行版版本。

原始机器身份仅在采集与派生函数内部短暂使用，不进入 DeviceInfo、异常、repr、日志或序列化结果。

### 4.2 生命周期

导入模块不采集、不执行命令、不写文件。collect_device 为显式同步 I/O 调用；调用方在客户端初始化阶段执行一次并保存结果，不在每个请求重复采集。

核心不建立跨 namespace 的无限全局缓存，不缓存失败到磁盘。需要重试时调用者重新采集；SDK 对 unavailable 结果如何提醒、请求是否继续，属于 SDK 适配层。本库不替宿主应用决定。

异步应用在启动阶段或工作线程调用，不在每个请求的事件循环中运行系统工具。首期无需再封装一套异步 API。

## 5 eapi 归属与文件组织

核心归属 eapi 的 backend 区域，但独立轻量打包，避免把 FastAPI 基础设施带进 SDK。建议新增：

| 路径 | 职责 |
| --- | --- |
| backend/packages/device-fingerprint/pyproject.toml | 轻量发行单元，名称暂定 dwy-device-fingerprint，Python >=3.9，零运行时依赖 |
| backend/packages/device-fingerprint/src/dwy_device/__init__.py | 公开 collect_device 与本库类型 |
| backend/packages/device-fingerprint/src/dwy_device/models.py | DeviceInfo、SystemInfo 与明确错误枚举 |
| backend/packages/device-fingerprint/src/dwy_device/collector.py | 参数校验、平台分发、规范化与 HMAC 派生 |
| backend/packages/device-fingerprint/src/dwy_device/providers/windows.py | Windows 系统来源 |
| backend/packages/device-fingerprint/src/dwy_device/providers/macos.py | macOS 系统来源 |
| backend/packages/device-fingerprint/src/dwy_device/providers/linux.py | Linux 系统来源 |
| backend/packages/device-fingerprint/tests/ | 核心契约、平台适配与分发测试 |
| backend/src/dwyeapi/device.py | eapi 可选门面，复用核心，不复制实现 |

三平台采用明确分发，无动态插件注册、反射扫描或 BaseProvider 继承框架。后续支持新系统时新增 provider 文件及一处分发映射。

eapi 可提供 `[device]` 可选依赖，显式使用 `dwyeapi.device` 时才加载核心；不在 eapi 根入口强制导入可选模块。核心项目不反向 import dwyeapi，避免循环依赖。

内部 Python 3.9 应用直接使用 `dwy_device`；已安装 eapi 的 Python 3.11+ 应用可通过 `dwyeapi.device` 使用同一契约。独立轻包测试避免加载 eapi 的全局 conftest 和后端基础设施。

## 6 分发与 SDK 接入边界

内部应用通过私有 Release 的固定版本轻量 wheel 复用；现有私有工作流和发布清单需增加该产物。核心与 eapi 门面一并进行契约验证，不修改仓库私有分发政策。

公开 QuantZone SDK 不能把私有 dwyeapi 或私有轻包直接列为普通 PyPI 运行时依赖，否则用户安装时无法解析。提高 SDK 最低 Python 版本也不能解决私有依赖问题。

如果后续接入公开 SDK，建议使用构建阶段内嵌共享模块：固定私有 Release 版本与摘要，在受控构建环境取得核心，将唯一实现打入 SDK wheel，保留来源版本和必要许可证；不得长期手工维护两份实现。构建身份及跨私有仓库读取方式届时按现有 CI 权限配置，不把凭据写进包或下载 URL。

公开 SDK 内嵌意味着会向 SDK 用户分发这部分实现，必须先明确允许对外分发的模块范围；本轮只设计并保存在私有仓库，不自动将核心公开发布，也不修改 SDK 分发方式。若希望公共 PyPI 独立轻包，需要先改变现有私有分发约束，不能由本方案默认执行。

## 7 验证与文档

按基础库规则先写测试再实现，并同步 backend/TEST_CASES.md 与核心使用文档。新增可选门面或调整公开导出时验证 eapi 全量测试；核心测试独立运行 Python 3.9 及受支持新版矩阵。

| 类别 | 验证内容 |
| --- | --- |
| 固定向量 | 已知原始身份与 namespace 的 HMAC 输出固定，三个平台规范化结果一致 |
| 应用隔离 | 同 namespace 稳定，不同 namespace 不同，OS 元数据变化不改指纹 |
| 环境隔离 | 同系统身份跨账号配置、进程、项目和 venv 得到同结果 |
| Windows | 64 位注册表视图、32/64 位 Python、权限、缺失、无效 UUID |
| macOS | plist 解析、属性缺失、超时、非零退出、超长输出，Intel 与 Apple Silicon |
| Linux | 两文件路径优先级、主文件非法/无权限、不存在、全零和超长内容 |
| 失败语义 | unavailable/unsupported 不生成随机 ID，不泄露原始身份或命令输出 |
| 无副作用 | import 不执行系统命令、不访问网络、不写磁盘 |
| 真实运行 | Windows/macOS/Linux runner 或真实设备读取，重复进程验证稳定 |
| 分发 | 轻包可在 Python 3.9 安装导入，不拉 FastAPI 等依赖；eapi 可选门面缺依赖时给明确安装提示 |

CI runner 只能说明该 runner 的系统来源可读及身份稳定，不能据此宣称识别物理宿主或所有容器。SDK 发布包联调属于后续接入验收。

## 8 推荐结论

推荐“参考 py-machineid、Go machineid、node-machine-id，标准库做固定原生适配”，不直接包装不可控自动回退。核心归属 eapi，独立为 Python >=3.9 的零运行时依赖轻包；eapi 通过可选门面复用。失败返回明确状态，不降级为随机安装 ID。

本轮方案待审阅的两个取舍：是否采用原生适配而非直接依赖 py-machineid；是否采用 eapi 下独立轻包而非把全部实现绑定到 dwyeapi 发行包。公开 SDK 的内嵌分发范围在接入时单独明确。
