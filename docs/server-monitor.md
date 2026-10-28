# 轻量服务器采集与告警

`backend/tools/server_monitor.py` 是独立 Python 模块，只依赖 `psutil==7.2.2`，不导入 dwyeapi，不需要 Docker、数据库或 HTTP 服务。Python 需要 3.11 及以上。

## 先采集一次

在仓库根运行：

```bash
uv run backend/tools/server_monitor.py --once
```

uv 按脚本声明创建独立依赖环境，不安装整个后端。也可以把这个文件单独复制到服务器执行。

已有 Python 虚拟环境时：

```bash
python -m pip install "psutil==7.2.2"
python backend/tools/server_monitor.py --once --path / /data
```

输出一行 JSON，包含 `hostname`、UTC `timestamp` 和 `metrics`：`cpu`、`memory`、`disk:/` 等值均为百分比。CPU 采样阻塞一秒；内存使用 psutil 的 `(total - available) / total` 口径，包含对可回收缓存的处理。磁盘读取指定路径所属文件系统的使用率，不计算目录大小。

`--once` 始终只采集，即使设置了 Webhook 环境变量也不会推送。磁盘路径不存在或不可访问时返回退出码 1。

## 定时告警

发送地址从环境变量 `SERVER_MONITOR_WEBHOOK_URL` 读取；下面是占位地址，替换成自己的 Discord Webhook：

```bash
export SERVER_MONITOR_WEBHOOK_URL='https://discord.com:443/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN'
uv run backend/tools/server_monitor.py --path / /data
```

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `--interval` | `60` | 采样周期，单位秒 |
| `--cpu` | `90` | CPU 使用率告警阈值 |
| `--memory` | `90` | 内存使用率告警阈值 |
| `--disk` | `80` | 每个指定文件系统的使用率告警阈值 |
| `--path` | `/` | 一个或多个路径，例如 `--path / /data` |
| `--cooldown` | `1800` | 同一指标持续超限时，重复通知的间隔秒数 |
| `--format` | `discord` | `discord` 消息或通用 `json` 事件 |

达到阈值即告警，默认不要求持续五分钟。低于阈值五个百分点（含等于）时发送一次恢复通知，例如磁盘 80% 告警、75% 恢复。CPU、内存和各磁盘分别维护状态。每轮采集结果也会写到标准输出。

Webhook 请求有十秒超时，不跟随重定向。发送成功后才更新告警状态；失败会输出脱敏错误并在下一轮仍满足条件时重试，不生成历史消息队列。HTTP 429 同样等待下一轮，不解析额外的重试时间。单轮采集或发送耗时超过配置周期时，下一轮会顺延。

通用 Webhook 示例：

```bash
export SERVER_MONITOR_WEBHOOK_URL='https://example.com:443/hooks/server-monitor'
uv run backend/tools/server_monitor.py --format json
```

接收端需要接受下面的 JSON；各平台格式不同，`json` 模式不代表自动兼容所有聊天客户端：

```json
{
  "hostname": "web-01",
  "timestamp": "2026-10-28T00:00:00+00:00",
  "metric": "disk:/",
  "value": 82.5,
  "threshold": 80,
  "status": "alert"
}
```

恢复事件的 `status` 为 `recovered`。Discord 模式禁用自动 @mention。

## 在 Linux 上常驻

只需复制 `backend/tools/server_monitor.py`。以下 `/opt/dwy-monitor` 是服务器安装目录示例：

```bash
sudo install -d /opt/dwy-monitor
sudo install -m 644 backend/tools/server_monitor.py /opt/dwy-monitor/server_monitor.py
sudo python3 -m venv /opt/dwy-monitor/.venv
sudo /opt/dwy-monitor/.venv/bin/python -m pip install "psutil==7.2.2"
```

创建 `/etc/dwy-monitor.env`，填写自己的地址，并将权限设为 `600`：

```dotenv
SERVER_MONITOR_WEBHOOK_URL=https://discord.com:443/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN
```

创建 `/etc/systemd/system/dwy-monitor.service`：

```ini
[Unit]
Description=DWY lightweight server monitor
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
DynamicUser=yes
EnvironmentFile=/etc/dwy-monitor.env
ExecStart=/opt/dwy-monitor/.venv/bin/python /opt/dwy-monitor/server_monitor.py --path /
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo chmod 600 /etc/dwy-monitor.env
sudo systemctl daemon-reload
sudo systemctl enable --now dwy-monitor.service
sudo journalctl -u dwy-monitor.service -f
```

需要监控数据盘时，在 `ExecStart` 的 `--path` 后补上对应挂载点。服务用户需要能访问这些路径；如果启用了隔离挂载命名空间，应确认服务看到的是预期的宿主文件系统。

## 作为模块复用

把同一个脚本放到应用可导入的目录后：

```python
from server_monitor import Monitor, WebhookSender, collect_metrics
import os

monitor = Monitor(WebhookSender(os.environ["SERVER_MONITOR_WEBHOOK_URL"]), disk=80)
metrics = collect_metrics(["/", "/data"])
monitor.check(metrics)
```

由调用方安排执行周期；这些接口是同步、单线程使用的。导入模块不会采集数据或发送网络请求。

告警状态只保存在内存，重启后仍超限会重新通知。单机断电、断网或采集器停止时无法自报故障；当前不包含外部心跳检测。尚未对实际服务器和真实 Discord 通道做部署验收。
