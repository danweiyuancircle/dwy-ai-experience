from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_original_platform_uses_verified_app_transaction():
    from dwy_apple_notify.apple import apple_original_platform

    client = SimpleNamespace(get_app_transaction_info=AsyncMock(
        return_value=SimpleNamespace(signedAppTransactionInfo="signed")
    ))
    verify = AsyncMock(return_value=SimpleNamespace(originalPlatform="macOS"))
    assert await apple_original_platform(client, verify, "123") == "macOS"
    verify.assert_awaited_once_with("signed")

    verify.return_value = SimpleNamespace(originalPlatform=None)
    assert await apple_original_platform(client, verify, "123") is None
