# 微信支付通知来源测试

`tests/test_notifications.py`（30 cases）：

| 用例 | 验证 |
| --- | --- |
| test_real_sdk_verifies_payment_and_refund_without_appid ×4 | 临时 RSA 签名+AESGCM，真实 SDK callback；付款及退款 SUCCESS/ABNORMAL/CLOSED，退款无 appid |
| test_untrusted_callback_rejected_without_sensitive_error ×13 | 错误签名、SIGNTEST、错误密钥/商户/应用/金额/币种/状态，bool金额、缺字段、超长标识、退款事件状态不符、退款显式非 CNY |
| test_sdk_none_and_exception_are_safe | SDK 返回 None/抛异常安全拒绝，不泄漏 SDK 错误 |
| test_confirmed_and_callback_share_business_key_without_fabricated_official_id | 回调与宿主确认结果同键；查单不伪造官方 ID；退款状态独立键 |
| test_strict_models_and_utf8_content_budget | 字段限长、非空身份、退款必填、上下文类型与限长、1800 UTF8 bytes、金融标识完整、整数金额 |
| test_installer_acknowledges_duplicates_but_retries_sink_failure_and_limits_stream | sink 失败 503、重复 204、原文一次验签、分块超限 413、SIGNTEST 400 |
| test_core_import_does_not_import_fastapi_or_host_payment | 新进程核心导入不加载 FastAPI/宿主支付 |
| test_host_result_subclass_keeps_sensitive_extensions_out_of_event_data | 宿主结果子类的 openid/secret 扩展字段不能进入事件 data；出口固定白名单 |
| test_confirmed_rejects_invalid_financial_amounts ×4 | 零金额、字符串金额、零退款、超额退款 |
| test_verifier_rejects_oversize_before_callback | 原始 bytes 超限不调用 SDK |
| test_verifier_bounds_signature_header_before_sdk | 签名头超限不调用 SDK；已知签名相关头均限制长度 |
| test_installer_preserves_lifecycle_and_refuses_conflicting_routes | 保留宿主 lifespan，拒绝重复安装/同路径冲突 |

`tests/wheel_smoke.py`：已安装 wheel 核心导入/公共版本/统一键/隐私字段合同。真实微信交易、退款、企微发送、生产持久队列与部署验收不属于本地测试。
