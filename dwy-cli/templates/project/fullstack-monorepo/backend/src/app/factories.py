"""Provider 工厂 -- 按 settings 选择外部服务的具体实现。

业务包只依赖 Protocol(在各包 protocols.py 定义),具体实现由本文件根据
settings.environment / settings.<domain>.provider 等字段决定:
  - dev: 内存实现(InMemorySmsProvider 等)
  - prod: 真实实现(AliyunSmsProvider / TencentOssProvider 等)

main.py 调用本文件的 make_* 函数,把 Provider 注入业务包的 register()。
"""

# 示例占位:实际新增业务时,在此添加 make_xxx_provider(settings) -> XxxProvider
#
# def make_sms_provider(settings: Settings) -> SmsProvider:
#     if settings.environment == "dev":
#         return InMemorySmsProvider()
#     return AliyunSmsProvider(access_key=settings.sms.access_key, ...)
