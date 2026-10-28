# dwy-device-fingerprint

eapi 体系下独立的跨平台设备指纹核心，Python 3.9+，零运行时依赖。只采集并返回结果，不联网、不记录设备日志、不执行限制策略。

## 安装与使用

源码仓库根目录安装：

```bash
uv pip install ./backend/packages/device-fingerprint
```

安装公开 PyPI 已发布版本：

```bash
python -m pip install dwy-device-fingerprint
```

完整示例只打印采集状态，不把设备指纹写入日志：

```python
from dwy_device import collect_device


def device_headers() -> dict[str, str]:
    """客户端初始化时采集一次，后续请求复用结果。"""
    info = collect_device("example.app", command_timeout=2.0)
    if info.fingerprint is None:
        return {}
    return {"X-Device-Id": info.fingerprint}


if __name__ == "__main__":
    headers = device_headers()
    print("available" if headers else "unavailable")
```

`namespace` 必须为 1 至 128 个小写 ASCII 字母、数字、点、下划线或连字符，产品与其 SDK/桌面端使用同一固定值。`command_timeout` 为有限正数，最大 30 秒；非法调用参数抛 ValueError。

### 返回结果

`DeviceInfo` 与 `SystemInfo` 是本库不可变 dataclass，状态、来源和错误使用本库 str Enum。

| 字段 | 内容 |
| --- | --- |
| fingerprint | 可用时 64 位小写十六进制，否则 None |
| scheme_version | 1 |
| source | Windows MachineGuid、macOS IOPlatformUUID 或 Linux machine-id 的明确来源 |
| status | available、unavailable、unsupported |
| error_code | 无错误为 None；否则为缺失、权限、超时、无效值、命令失败或不支持平台 |
| system | system_name、system_release、system_version、architecture |

系统信息来自 platform 标准库，Darwin/Linux 的 release 为内核发行信息，不代表产品营销版本。原始机器身份不包含在结果中。

### 稳定性

- Windows 使用 64 位注册表 MachineGuid；macOS 读取 ioreg 的 IOPlatformUUID；Linux 优先 /etc/machine-id，仅缺失时读取 /var/lib/dbus/machine-id。
- 规范化机器身份作为 HMAC-SHA256 key，`dwy.device.v1:` 加 namespace 作为 message。不同产品域隔离，同产品域跨账号配置、进程、项目和 venv 保持一致。
- OS 元数据和 SDK 版本不参与派生。原始系统身份、namespace 或方案版本改变会影响结果。
- 无可靠来源时返回结构化失败，不降级到随机值、MAC、hostname 或安装文件；不自动重试、不缓存到磁盘。需要缓存时由客户端实例保存结果。
- 容器、虚拟机、WSL 只识别当前系统环境，不能保证物理宿主唯一。克隆镜像、重装系统或修改客户端可以绕过，指纹不用于身份认证。
- 本接口包含同步系统 I/O；异步应用在初始化或工作线程调用，不在每个请求中运行。

## eapi 可选门面

Python 3.11+ 且已安装匹配核心的 eapi 应用可以从 `dwyeapi.device` 导入同一入口和类型。eapi 根导入不强制加载设备模块。

EAPI 的公开版本提供 `device` extra：

```bash
python -m pip install 'dwyeapi[device]'
```

源码仓库公开，安装包通过 `.github/workflows/publish-device-fingerprint.yml` 公开发布。SDK 可以依赖固定版本的公开包，不需要源码仓库权限，也无需维护第二份实现。

## 测试与构建

在仓库根目录运行：

```bash
uv run --directory backend/packages/device-fingerprint --extra dev --frozen pytest
uv run --directory backend/packages/device-fingerprint --extra dev --frozen ruff check src tests
uv build --project backend/packages/device-fingerprint --default-index https://pypi.org/simple
```

macOS/Windows/Linux 原生读取测试需要设置 `DWY_DEVICE_NATIVE_TEST=1`；常规测试使用受控系统边界模拟，不打印真实原始身份。

运行时仅使用标准库。开源参考和许可见 THIRD_PARTY_NOTICES.md 与 LICENSE。
