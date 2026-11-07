"""查询由 Apple 签名的 App 交易事实。"""


async def apple_original_platform(client, verify, transaction_id: str) -> str | None:
    """使用官方客户端和调用方提供的异步验签器；调用方负责超时及错误处理。"""
    response = await client.get_app_transaction_info(transaction_id)
    transaction = await verify(response.signedAppTransactionInfo)
    value = getattr(transaction.originalPlatform, "value", transaction.originalPlatform)
    return value if value in {"iOS", "macOS", "tvOS", "visionOS"} else None
