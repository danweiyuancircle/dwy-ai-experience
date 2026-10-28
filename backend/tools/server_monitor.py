# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil==7.2.2"]
# ///
"""独立服务器采集与告警; 直接用 uv run 运行, 不加载 dwyeapi。"""

import argparse
import json
import math
import os
import socket
import sys
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

import psutil

Event = dict[str, str | float]


def collect_metrics(paths: Sequence[str] = ("/",)) -> dict[str, float]:
    """采集宿主机百分比; CPU 采样阻塞一秒, 磁盘路径必须可访问。"""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        **{f"disk:{path}": psutil.disk_usage(path).percent for path in paths},
    }


class WebhookError(RuntimeError):
    """发送失败的脱敏错误; 不携带 Webhook 地址、响应正文或凭据。"""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Webhook URL 可能包含凭据, 不能自动转发到其他地址。
        return None


class WebhookSender:
    """同步 JSON POST; 十秒超时、拒绝重定向, 失败由下一轮采样重试。"""

    def __init__(self, url: str, *, payload_format: str = "discord"):
        try:
            parts = urlsplit(url)
            valid = (
                parts.scheme in {"http", "https"}
                and parts.hostname
                and parts.port != 0
                and parts.username is None
                and parts.password is None
                and not parts.fragment
                and not any(character.isspace() for character in url)
            )
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("Webhook 必须是无用户名、密码和 fragment 的有效 HTTP(S) URL")
        if payload_format not in {"discord", "json"}:
            raise ValueError("Webhook 格式必须是 discord 或 json")
        self._url = url
        self._format = payload_format
        self._opener = build_opener(_NoRedirect())

    def __call__(self, event: Event) -> None:
        """2xx 视为接收成功; Discord 禁止 @mention, 通用模式直接发送事件 JSON。"""
        payload = event
        if self._format == "discord":
            content = (
                f"[{event['status']}] {event['hostname']} {event['metric']}: "
                f"{event['value']:.1f}% (告警阈值 {event['threshold']:.1f}%)"
            )
            payload = {"content": content[:2000], "allowed_mentions": {"parse": []}}
        request = Request(
            self._url,
            data=json.dumps(payload, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=10):
                pass
        except HTTPError as error:
            error.close()
            raise WebhookError(f"Webhook HTTP {error.code}") from None
        except (URLError, OSError, ValueError):
            raise WebhookError("Webhook 网络请求失败") from None


class Monitor:
    """单线程告警状态; 超限即时通知, 冷却后提醒, 下降五个百分点后通知恢复。"""

    def __init__(
        self,
        notify: Callable[[Event], None],
        *,
        cpu: float = 90,
        memory: float = 90,
        disk: float = 80,
        cooldown: float = 1800,
    ):
        self._thresholds = {"cpu": cpu, "memory": memory, "disk": disk}
        if any(not math.isfinite(value) or not 0 < value <= 100 for value in self._thresholds.values()):
            raise ValueError("CPU、内存和磁盘阈值必须在 (0, 100] 内")
        if not math.isfinite(cooldown) or cooldown <= 0:
            raise ValueError("告警冷却秒数必须为有限正数")
        self._notify = notify
        self._cooldown = cooldown
        self._hostname = socket.gethostname()
        # shortcut: 告警状态仅在内存中, 需跨重启去重时再持久化。
        self._alerted: dict[str, float] = {}

    def check(self, metrics: dict[str, float]) -> None:
        """接收 collect_metrics 的结果; 发送成功后才更新状态, 失败向调用者抛出。"""
        now = time.monotonic()
        for metric, value in metrics.items():
            threshold = self._thresholds[metric.split(":", 1)[0]]
            last_sent = self._alerted.get(metric)
            if value >= threshold and (last_sent is None or now - last_sent >= self._cooldown):
                status = "alert"
            elif last_sent is not None and value <= max(0, threshold - 5):
                status = "recovered"
            else:
                continue
            self._notify(
                {
                    "hostname": self._hostname,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "metric": metric,
                    "value": value,
                    "threshold": threshold,
                    "status": status,
                }
            )
            if status == "alert":
                self._alerted[metric] = now
            else:
                del self._alerted[metric]


def main(argv: Sequence[str] | None = None) -> int:
    """单次模式只输出 JSON; 常驻模式从 SERVER_MONITOR_WEBHOOK_URL 读取发送地址。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="采集一次并输出 JSON, 不发送 Webhook")
    parser.add_argument("--path", nargs="+", default=["/"], help="需要监控的磁盘路径, 默认 /")
    parser.add_argument("--interval", type=float, default=60, help="采样周期秒数, 默认 60")
    parser.add_argument("--cooldown", type=float, default=1800, help="同一告警重复提醒间隔秒数, 默认 1800")
    parser.add_argument("--cpu", type=float, default=90, help="CPU 告警百分比, 默认 90")
    parser.add_argument("--memory", type=float, default=90, help="内存告警百分比, 默认 90")
    parser.add_argument("--disk", type=float, default=80, help="磁盘告警百分比, 默认 80")
    parser.add_argument("--format", choices=["discord", "json"], default="discord", help="Webhook 请求体格式")
    args = parser.parse_args(argv)
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("采样周期必须为有限正数")
    try:
        sender = None
        if not args.once:
            url = os.environ.get("SERVER_MONITOR_WEBHOOK_URL")
            if not url:
                parser.error("常驻模式需要设置 SERVER_MONITOR_WEBHOOK_URL")
            sender = WebhookSender(url, payload_format=args.format)
        monitor = Monitor(
            sender if sender is not None else lambda event: None,
            cpu=args.cpu,
            memory=args.memory,
            disk=args.disk,
            cooldown=args.cooldown,
        )
    except ValueError as error:
        parser.error(str(error))
    try:
        while True:
            started = time.monotonic()
            try:
                metrics = collect_metrics(args.path)
                print(
                    json.dumps(
                        {
                            "hostname": socket.gethostname(),
                            "timestamp": datetime.now(UTC).isoformat(),
                            "metrics": metrics,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                if args.once:
                    return 0
                monitor.check(metrics)
            except (OSError, WebhookError) as error:
                message = str(error) if isinstance(error, WebhookError) else "指标采集失败, 请检查磁盘路径和权限"
                print(message, file=sys.stderr, flush=True)
                if args.once:
                    return 1
            time.sleep(max(0, args.interval - (time.monotonic() - started)))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
