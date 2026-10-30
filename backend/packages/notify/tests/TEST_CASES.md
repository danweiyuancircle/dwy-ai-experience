# 通知包测试用例

- `tests/test_appearance.py`：发送者名称必填，单目标、多目标及其它渠道缺名时全部在网络前拒绝，正文标题不能代替名称；头像可省略或显式 null。按字段校验单次/应用/URL/业务预设优先级、名称不可清空、并发隔离、指纹稳定及不支持头像的其它渠道。拒绝控制字符、超长名称和非 HTTPS/带账号密码的头像地址。

执行：在 `backend/packages/notify/` 下运行 `python -m pytest tests/ -q`。

`tests/test_notify.py` 覆盖：

| 测试 | 验证 |
|---|---|
| `test_config_and_results_are_public_owned_and_frozen` | 非空 SecretStr 目标、有限正超时、frozen 配置、本包结果聚合 |
| `test_discord_sends_once_without_mentions_embeds_redirect_retry_or_insecure_tls` | 单次 HTTP、安全 mentions、禁止嵌入预览、wait 确认 ID、安全参数覆盖 |
| `test_wecom_requires_integer_zero_business_result` | 非零、字符串、布尔、缺失、非法 JSON 结果均不能伪装成功 |
| `test_wecom_success_and_target_selection` | 企业微信成功、指定目标、摘要、未知与重复目标在请求前拒绝 |
| `test_http_failures_are_safe_structured_results` | 429 retry_after、永久 4xx、拒绝重定向、5xx、缺失 Discord ID |
| `test_network_error_and_logs_never_expose_url_or_body` | timeout / network_error 与插件日志秘密隔离 |
| `test_cancel_propagates_and_target_lock_covers_inflight_thread` | 取消传播，后台请求结束前同目标不并发 |
| `test_invalid_config_error_never_exposes_secret` | 无效 URL 错误不泄漏配置 |
| `test_standard_apprise_http_channels_force_safety_and_isolate_logger` | 钉钉、飞书继承安全参数，失败不受 optional 影响，宿主 logger 不变 |
| `test_non_http_or_insecure_protocol_is_rejected` | SMTP 和明文 HTTP 协议拒绝 |
| `test_native_discord_url_and_second_message_keep_real_confirmation` | 原生 Discord URL 与复用实例连续发送 |
| `test_different_targets_send_concurrently_and_preserve_config_order` | 不同目标并发，返回顺序稳定 |
| `test_unexpected_sdk_response_errors_are_safe_delivery_failures` | 第三方异常不能泄漏 URL 或原始异常 |
| `test_discord_split_stops_after_first_failure_and_retains_its_error` | 分段首个请求失败后不继续发送并保留原结果 |
| `test_plugins_with_internal_retries_are_rejected` | Fluxer、Revolt、Matrix、SparkPost、SendPulse 内部重试渠道拒绝 |
| `test_discord_response_id_must_be_bounded_ascii_digits` | Discord 响应 ID 拒绝 Unicode 数字和超过 128 位的值 |
| `test_timeout_rejects_boolean_nonfinite_and_unbounded_values` | 超时严格拒绝布尔、非有限和超过 30 秒的值 |
| `test_invalid_send_input_is_rejected_before_http` | 空白／非字符串正文、非字符串标题、空或错误类型目标拒绝 |
| `test_http_debug_logging_is_suppressed_only_in_notification_thread` | HTTP 调试日志的 URL／正文隔离，保留普通宿主日志 |

网络均为模拟响应；真实 Discord / 企业微信投递、全部 Apprise 插件未验收。
