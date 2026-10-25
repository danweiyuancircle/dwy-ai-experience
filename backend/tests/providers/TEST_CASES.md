# Email Provider 回归用例

运行：在 `backend/` 执行 `.venv/bin/python -m pytest tests/providers -q`。

既有工厂、域名策略、Redis 验证码与 SDK 异常用例共 30 项，原清单保留在 `backend/TEST_CASES.md` 第 10.1、13 节。

## 邮件中英文（`test_email_language.py`，8 项）

| 用例 | 验证行为 |
|---|---|
| `test_language_selects_complete_message[None]` | 省略语言时，主题、HTML 和纯文本均为英文，验证码和有效期一致 |
| `test_language_selects_complete_message[en]` | 显式英文完整覆盖正文、安全提示和客服说明 |
| `test_language_selects_complete_message[zh]` | 显式中文保留中文主题、原有正文及 `lang="zh-CN"` |
| `test_concurrent_languages_do_not_change_shared_provider` | 同一实例并发中英文发信，语言与验证码不串用；调用方生成的码不访问 Redis |
| `test_factory_forwards_localized_subject_and_brand_copy` | 工厂透传英文主题、副标语和页脚配置；中文配置仍生效 |
| `test_english_omits_untranslated_tagline_and_slogan` | 未配置英文宣传文案时省略中文宣传文案，品牌名保留 |
| `test_localized_html_escapes_brand_and_code[zh]` | 中文模板对品牌名、副标语、页脚和验证码保留 HTML 转义 |
| `test_localized_html_escapes_brand_and_code[en]` | 英文模板对品牌名、副标语、页脚和验证码保留 HTML 转义 |

## 自定义通道接口

`send_code`、`send_verification_code`、`_send` 和两个模板方法的语言参数均为 keyword-only `language="en"`。
只有归一化的 `"zh"` 选择中文。自定义 `_send` 必须接受并透传该参数，禁止存入共享实例状态。
