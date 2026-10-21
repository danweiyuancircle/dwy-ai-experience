# 跨平台设备指纹实现计划

**Goal:** 在 eapi 体系内交付 Python 3.9+、零运行时依赖的设备指纹核心及可选门面。

**Architecture:** 标准库原生采集固定系统身份，规范化后使用带产品域的 HMAC-SHA256。核心独立发行，eapi 可选导入；同步补私有构建和跨系统 CI，不接入公开 SDK。

**Tech Stack:** Python 标准库、setuptools、pytest、ruff、GitHub Actions。

**Spec:** docs/superpowers/specs/2026-10-21-device-fingerprint-design.md

## 全局约束

- 核心 Python >=3.9，无运行时依赖，eapi 保持 Python >=3.11。
- namespace 为 1..128 个小写 ASCII 字母、数字、点、下划线或连字符。
- command_timeout 默认 2.0 秒，仅接受有限正数，最大 30 秒。
- HMAC key 为规范化 32 位机器身份 ASCII，message 为 dwy.device.v1: 加 namespace 的 UTF-8 字节。
- 采集失败返回类型化状态，不生成随机身份、不导出原始身份、不写文件或网络、不在 import 阶段采集。
- 保留既有提交，在 codex/eapi-device-fingerprint 分支实现；按用户后续授权提交推送，不发布版本。

## 审阅重点

- Linux 主文件存在但非法/无权限时不使用另一文件掩盖问题。
- macOS 子进程超时、畸形或超长 plist 不泄露输出，不滞留子进程。
- Windows 使用 64 位注册表视图，离开 Windows 时导入包不触发 winreg 导入失败。
- 缺可选依赖时 eapi 基础导入可用；安装轻包不会拉入 FastAPI。
- 真实设备验收只显示状态与来源，不输出原始身份和指纹。

## Task 1 核心契约与 Linux 采集

**Files:** backend/packages/device-fingerprint/src/dwy_device/{__init__,models,collector}.py、providers/{__init__,_errors,linux}.py、tests/test_collector.py、tests/test_linux.py。

**Interfaces:** 公开 collect_device(namespace: str, *, command_timeout: float = 2.0) -> DeviceInfo；DeviceInfo/SystemInfo 为 frozen dataclass。DeviceSource、DeviceStatus、DeviceErrorCode 为 str Enum。私有 CollectionError(code: DeviceErrorCode) 只存安全错误码。平台 provider 的 read_machine_id 返回 tuple[str, DeviceSource]，采集失败抛 CollectionError。

- [x] 先写测试：固定向量、namespace/timeout 边界、元数据不参与派生、失败状态、原始值不进入返回对象、Linux 路径优先级和有界读取。
- [x] 运行失败用例，确认缺失功能导致失败。
- [x] 实现最小核心及 Linux provider，其他平台通过延迟导入接入。
- [x] 运行核心用例并记录结果。

## Task 2 Windows 与 macOS provider

**Files:** backend/packages/device-fingerprint/src/dwy_device/providers/{windows,macos}.py、tests/test_windows.py、tests/test_macos.py。

**Interfaces:** Windows read_machine_id()；macOS read_machine_id(command_timeout: float)。返回 tuple[str, DeviceSource]，沿用 Task 1 类型及 CollectionError。

- [x] 先写测试，运行并确认缺失 provider 导致失败。
- [x] Windows 标准库 winreg 读取 64 位 MachineGuid，限制类型与长度，错误映射为安全错误码。
- [x] macOS 使用固定 ioreg、shell=False、有限超时和有界输出，plistlib 解析 UUID；错误不得携带命令输出。
- [x] 验证超时、非零退出、缺失、权限、格式和输出上限。

## Task 3 轻包、eapi 门面与私有构建

**Files:** backend/packages/device-fingerprint/pyproject.toml、README.md、LICENSE、THIRD_PARTY_NOTICES.md、backend/src/dwyeapi/device.py、backend/pyproject.toml、backend/tests/test_device.py、.github/workflows/private-release.yml、独立设备 CI 工作流、backend/README.md、backend/TEST_CASES.md、backend/CHANGELOG.md。

**Interfaces:** dwy-device-fingerprint 首版 0.1.0，eapi [device] extra 精确依赖核心 0.1.0；仅显式导入 dwyeapi.device 才要求安装核心，不在 eapi 根入口增加强导入。核心打包不包含测试或后端环境依赖。

- [x] 先写门面可用/缺依赖提示测试，确认失败。
- [x] 实现可选门面、独立包元数据和文档；补私有 Release 构建产物及 Python 3.9/受支持新版与三系统 CI。
- [x] 在现有本地环境安装本地核心，无网络安装运行时依赖；同步现有锁文件所需配置。
- [x] 核心全量测试、eapi 全量测试、发布脚本测试、ruff 通过。
- [x] 构建 wheel/sdist，隔离验证 Python 3.9 安装导入与零依赖，macOS 本机真实采集两进程比较但不打印指纹。

## Task 4 审阅与交付

- [x] 独立审阅契约、安全边界、打包和工作流，修复实质问题并补回归。
- [x] 更新计划勾选与实际验证结果，检查 diff 和未提交范围。
- [x] 报告实现入口、验证结果及 Windows/Linux 真实运行待 CI 验收边界。

## 实际验证记录

- 基线 eapi 250 项通过；新增门面后 253 项通过，保留基线已有 2 条 Starlette 弃用警告。
- 核心 74 项常规测试通过；启用 macOS 原生验收后 75 项通过。Python 3.9.6 与 3.15.0 均完成 75 项测试。
- 独立 Python 3.9 环境以 --no-deps 安装 wheel，隔离模式导入与真实采集成功，不加载 FastAPI/Pydantic/eapi。
- 核心 wheel/sdist 构建通过，wheel 包含 py.typed、MIT 与参考声明且不含测试；eapi wheel 包含可选门面及精确核心 extra 依赖。
- Ruff check/format、两份 YAML 解析、发布脚本测试和两份锁文件一致性检查通过。
- CI 明确覆盖 Windows x86/x64、macOS Intel/Apple Silicon 和 Linux；Python 补丁号按官方 Actions 二进制清单分别固定，尚未触发远程 CI。
- Windows/Linux 原生来源和 macOS Intel 仍待远程 runner 验收；实现验收后按用户授权提交推送，未发布或改 QuantZone SDK。
