# 服务器监控模块测试

运行独立测试，不加载后端服务或其 fixtures：

```bash
uv run --no-project --with "psutil==7.2.2" --with "pytest==9.0.3" python -m pytest backend/tools/tests -q
```

测试文件：`backend/tools/tests/test_server_monitor.py`。

| 测试 | 验证行为 |
| --- | --- |
| `test_once_collects_real_host_without_webhook` | 当前系统真实采集、JSON 输出、百分比范围，无需 Webhook |
| `test_collects_cpu_interval_memory_pressure_and_each_disk` | CPU 一秒采样、内存百分比、逐路径磁盘采集 |
| `test_alerts_at_threshold` | CPU、内存、磁盘等于阈值时告警 |
| `test_healthy_values_send_nothing` | 健康指标不通知 |
| `test_cooldown_and_reminders` | 冷却期去重，到期提醒 |
| `test_recovery_hysteresis_and_realert_per_disk` | 各磁盘独立、五个百分点恢复迟滞、恢复后重新告警 |
| `test_failed_delivery_does_not_advance_state` | 告警或恢复发送失败后保留可重试状态 |
| `test_webhook_posts_real_http_payload` | 向本地 HTTP 服务实际发送 Discord 与通用 JSON，请求格式和 @mention 限制 |
| `test_http_errors_are_sanitized_and_redirects_are_not_followed` | 302/400/429/500 不误报成功、不跟随重定向、不泄露地址凭据 |
| `test_invalid_webhook_urls_do_not_echo_credentials` | 拒绝非 HTTP(S)、缺主机、URL 用户名密码和非法端口 |
| `test_network_failure_is_sanitized` | 网络失败使用十秒超时，异常不携带 Webhook 凭据 |
| `test_daemon_continues_after_delivery_failure` | 常驻循环在投递失败后继续采集并重试，正常响应中断退出 |
| `test_once_inaccessible_path_has_clean_failure` | 采集失败返回退出码 1，无 traceback 或不完整 JSON |
| `test_invalid_monitor_configuration_is_rejected` | 阈值范围、NaN、无穷值及非法冷却时间 |
| `test_cli_rejects_invalid_configuration` | CLI 参数错误返回退出码 2，无 traceback |
| `test_daemon_requires_webhook_env` | 常驻模式缺少 Webhook 配置时立即失败 |

自动检查见 `.github/workflows/server-monitor.yml`。真实采集测试只证明当前操作系统可读，不代表远程 Linux 或真实 Discord 投递已验收。
