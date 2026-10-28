"""独立采集、告警状态与真实 HTTP 边界测试, 不加载后端服务。"""

import importlib.util
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "server_monitor.py"


@pytest.fixture(scope="module")
def monitor_module():
    spec = importlib.util.spec_from_file_location("server_monitor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def endpoint():
    requests = []
    response = {"status": 204}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.path, self.headers["Content-Type"], payload))
            self.send_response(response["status"])
            self.send_header("Location", "/redirect-target")
            self.end_headers()

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/hook/SECRET", requests, response
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_once_collects_real_host_without_webhook():
    result = subprocess.run([sys.executable, str(SCRIPT), "--once"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    sample = json.loads(result.stdout)
    assert sample["hostname"]
    assert sample["timestamp"]
    assert set(sample["metrics"]) == {"cpu", "memory", "disk:/"}
    assert all(0 <= value <= 100 for value in sample["metrics"].values())


def test_collects_cpu_interval_memory_pressure_and_each_disk(monitor_module, monkeypatch):
    psutil = monitor_module.psutil
    memory = psutil.virtual_memory()._replace(percent=42)
    disk = psutil.disk_usage("/")

    def cpu_percent(*, interval):
        assert interval == 1
        return 12.5

    monkeypatch.setattr(psutil, "cpu_percent", cpu_percent)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(psutil, "disk_usage", lambda path: disk._replace(percent={"/": 80, "/data": 95}[path]))
    assert monitor_module.collect_metrics(["/", "/data"]) == {
        "cpu": 12.5,
        "memory": 42,
        "disk:/": 80,
        "disk:/data": 95,
    }


@pytest.mark.parametrize(("metric", "value"), [("cpu", 90), ("memory", 90), ("disk:/", 80)])
def test_alerts_at_threshold(monitor_module, metric, value):
    events = []
    monitor = monitor_module.Monitor(events.append)
    monitor.check({metric: value})
    assert len(events) == 1
    assert events[0]["status"] == "alert"
    assert events[0]["metric"] == metric
    assert events[0]["value"] == value
    assert events[0]["threshold"] == value


def test_healthy_values_send_nothing(monitor_module):
    events = []
    monitor_module.Monitor(events.append).check({"cpu": 89, "memory": 89, "disk:/": 79})
    assert events == []


def test_cooldown_and_reminders(monitor_module, monkeypatch):
    events = []
    now = [0]
    monkeypatch.setattr(monitor_module.time, "monotonic", lambda: now[0])
    monitor = monitor_module.Monitor(events.append, cooldown=60)
    monitor.check({"disk:/": 80})
    now[0] = 59
    monitor.check({"disk:/": 95})
    assert len(events) == 1
    now[0] = 60
    monitor.check({"disk:/": 96})
    assert [event["value"] for event in events] == [80, 96]


def test_recovery_hysteresis_and_realert_per_disk(monitor_module):
    events = []
    monitor = monitor_module.Monitor(events.append)
    monitor.check({"disk:/": 80, "disk:/data": 90})
    monitor.check({"disk:/": 79, "disk:/data": 90})
    assert len(events) == 2
    monitor.check({"disk:/": 75, "disk:/data": 90})
    monitor.check({"disk:/": 80, "disk:/data": 90})
    assert [(event["metric"], event["status"]) for event in events] == [
        ("disk:/", "alert"),
        ("disk:/data", "alert"),
        ("disk:/", "recovered"),
        ("disk:/", "alert"),
    ]


@pytest.mark.parametrize("recover", [False, True])
def test_failed_delivery_does_not_advance_state(monitor_module, recover):
    events = []
    failing = [False]

    def send(event):
        if failing[0]:
            raise monitor_module.WebhookError("unavailable")
        events.append(event)

    monitor = monitor_module.Monitor(send)
    if recover:
        monitor.check({"disk:/": 80})
    value = 75 if recover else 80
    failing[0] = True
    with pytest.raises(monitor_module.WebhookError):
        monitor.check({"disk:/": value})
    failing[0] = False
    monitor.check({"disk:/": value})
    assert events[-1]["status"] == ("recovered" if recover else "alert")


@pytest.mark.parametrize("payload_format", ["discord", "json"])
def test_webhook_posts_real_http_payload(monitor_module, endpoint, payload_format):
    url, requests, _ = endpoint
    event = {"hostname": "test-host", "metric": "disk:/", "value": 80, "threshold": 80, "status": "alert"}
    monitor_module.WebhookSender(url, payload_format=payload_format)(event)
    assert len(requests) == 1
    path, content_type, body = requests[0]
    assert path == "/hook/SECRET"
    assert content_type == "application/json"
    if payload_format == "json":
        assert body == event
    else:
        assert "test-host" in body["content"]
        assert "disk:/" in body["content"]
        assert "80.0%" in body["content"]
        assert body["allowed_mentions"] == {"parse": []}


@pytest.mark.parametrize("status", [302, 400, 429, 500])
def test_http_errors_are_sanitized_and_redirects_are_not_followed(monitor_module, endpoint, status):
    url, requests, response = endpoint
    response["status"] = status
    with pytest.raises(monitor_module.WebhookError) as error:
        monitor_module.WebhookSender(url)(
            {"hostname": "host", "metric": "cpu", "value": 95, "threshold": 90, "status": "alert"}
        )
    assert str(status) in str(error.value)
    assert "SECRET" not in str(error.value)
    assert len(requests) == 1


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "https:///hook", "https://user:SECRET@example.com/hook", "http://localhost:invalid/hook"],
)
def test_invalid_webhook_urls_do_not_echo_credentials(monitor_module, url):
    with pytest.raises(ValueError) as error:
        monitor_module.WebhookSender(url)
    assert "SECRET" not in str(error.value)


def test_network_failure_is_sanitized(monitor_module, monkeypatch):
    sender = monitor_module.WebhookSender("https://example.com/hook/SECRET")

    def unavailable(request, *, timeout):
        assert timeout == 10
        raise URLError("https://example.com/hook/SECRET")

    monkeypatch.setattr(sender._opener, "open", unavailable)
    with pytest.raises(monitor_module.WebhookError) as error:
        sender({"hostname": "host", "metric": "cpu", "value": 95, "threshold": 90, "status": "alert"})
    assert "SECRET" not in str(error.value)


def test_daemon_continues_after_delivery_failure(monitor_module, monkeypatch, capsys):
    url = "https://example.com/hook/SECRET"
    monkeypatch.setenv("SERVER_MONITOR_WEBHOOK_URL", url)
    samples = iter([{"disk:/": 80}, {"disk:/": 85}])
    attempts = []

    def send(_self, event):
        attempts.append(event)
        if len(attempts) == 1:
            raise monitor_module.WebhookError("Webhook HTTP 500")

    waits = []

    def sleep(seconds):
        waits.append(seconds)
        if len(waits) == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(monitor_module, "collect_metrics", lambda paths: next(samples))
    monkeypatch.setattr(monitor_module.WebhookSender, "__call__", send)
    monkeypatch.setattr(monitor_module.time, "sleep", sleep)
    assert monitor_module.main([]) == 0
    assert [event["value"] for event in attempts] == [80, 85]
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 2
    assert "Webhook HTTP 500" in captured.err
    assert "SECRET" not in captured.err


def test_once_inaccessible_path_has_clean_failure(monitor_module, monkeypatch, capsys):
    def unavailable(paths):
        raise PermissionError("permission denied")

    monkeypatch.setattr(monitor_module, "collect_metrics", unavailable)
    assert monitor_module.main(["--once"]) == 1
    captured = capsys.readouterr()
    assert not captured.out
    assert "采集失败" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "kwargs", [{"cpu": 0}, {"memory": 101}, {"disk": float("nan")}, {"cooldown": 0}, {"cooldown": float("inf")}]
)
def test_invalid_monitor_configuration_is_rejected(monitor_module, kwargs):
    with pytest.raises(ValueError):
        monitor_module.Monitor(lambda event: None, **kwargs)


@pytest.mark.parametrize("arguments", [["--interval", "0"], ["--interval", "nan"], ["--disk", "101"]])
def test_cli_rejects_invalid_configuration(arguments):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--once", *arguments], capture_output=True, text=True, check=False
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_daemon_requires_webhook_env(monkeypatch):
    monkeypatch.delenv("SERVER_MONITOR_WEBHOOK_URL", raising=False)
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "SERVER_MONITOR_WEBHOOK_URL" in result.stderr
