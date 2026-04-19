"""可插拔 Provider 扩展。

业务相关但复用性强的外部服务抽象(邮件、短信等),通过 Protocol + 配置驱动切换。
第三方 SDK 依赖一律走 optional-dependencies,业务项目 `pip install dwyeapi[email]` 按需启用。
"""
