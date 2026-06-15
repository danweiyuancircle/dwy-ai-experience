"""外部服务 Protocol 定义。

业务代码只依赖此处定义的 Protocol,具体实现由装配层 src/app/factories.py
按 settings.environment 选择(dev=in-memory,prod=real)。

示例:
    from typing import Protocol

    class SmsProvider(Protocol):
        async def send(self, phone: str, message: str) -> None: ...

    class OssProvider(Protocol):
        async def put(self, key: str, data: bytes) -> str: ...
"""
