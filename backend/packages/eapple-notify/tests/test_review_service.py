"""评论轮询的调度边界、失败隔离及通知文本测试。"""

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from dwy_apple_notify.reviews.delivery import ReviewDeliveryQueue
from dwy_apple_notify.reviews.formatting import baseline_content, review_content
from dwy_apple_notify.reviews.service import ReviewMonitor


def review(**changes):
    """测试无需真实 Apple 凭据或 HTTP 请求。"""
    return SimpleNamespace(id="r1", rating=2, title="连接问题", body="无法连接设备",
                           reviewer_nickname="tester", created_at=datetime(2026, 10, 1, tzinfo=UTC),
                           territory="CHN", **changes)


def monitor():
    """显式注入存储和采集器，避免调度器拥有任何项目资源。"""
    config = SimpleNamespace(apps={"123": SimpleNamespace(name="Demo")},
                             retention_days=30, poll_interval_seconds=3600)
    store = SimpleNamespace(cleanup=AsyncMock(), claim=AsyncMock(return_value="lease"),
                            complete=AsyncMock(return_value=True), release=AsyncMock())
    client = SimpleNamespace(list_reviews=AsyncMock(return_value=[review()]))
    return ReviewMonitor(config, store, client), store, client


async def test_due_app_syncs_with_configured_policy():
    """每轮清理保留期，并把可配置周期传到持久化调度。"""
    worker, store, client = monitor()
    assert await worker.run_once() == 1
    store.cleanup.assert_awaited_once_with(30)
    store.claim.assert_awaited_once_with("123", poll_interval_seconds=3600)
    client.list_reviews.assert_awaited_once_with("123")
    assert store.complete.await_args.kwargs["retention_days"] == 30
    assert store.complete.await_args.kwargs["poll_interval_seconds"] == 3600


async def test_not_due_skips_apple_but_still_cleans_history():
    """重启和重复 wake-up 不绕过数据库中的下次执行时间。"""
    worker, store, client = monitor()
    store.claim.return_value = None
    assert await worker.run_once() == 0
    client.list_reviews.assert_not_awaited()
    store.cleanup.assert_awaited_once()


async def test_failed_fetch_releases_lease_without_committing_partial_results():
    """分页失败不建立空基线，另一个应用仍可在同轮正常同步。"""
    worker, store, client = monitor()
    worker.config.apps["456"] = SimpleNamespace(name="Other")
    client.list_reviews.side_effect = [ValueError("secret must not be logged"), []]
    assert await worker.run_once() == 1
    assert client.list_reviews.await_count == 2
    assert store.complete.await_count == 1
    store.release.assert_awaited_once_with("123", "lease")


async def test_cancellation_propagates_and_releases_owned_lease():
    """停止服务不会吞掉取消，租约释放后可重新调度。"""
    worker, store, client = monitor()
    client.list_reviews.side_effect = asyncio.CancelledError
    with pytest.raises(asyncio.CancelledError):
        await worker.run_once()
    store.complete.assert_not_awaited()
    store.release.assert_awaited_once_with("123", "lease")


def test_notification_includes_rating_and_response_entry_without_exceeding_discord_limit():
    """长评论包含非 BMP 字符时仍受 Discord 消息长度约束。"""
    item = review()
    item.body = "😀" * 10000
    content = review_content("123", "Demo", item, updated=True)
    assert "2/5" in content and "已更新" in content
    assert "https://appstoreconnect.apple.com/apps/123" in content
    assert len(content.encode("utf-16-le")) // 2 <= 2000
    assert "历史" in baseline_content("123", "Demo", 4)


@pytest.mark.parametrize("updated,title", [
    (False, "新增评分评论"),
    (True, "评分评论已更新"),
])
def test_review_titles_distinguish_new_and_updated_ratings(updated, title):
    """标题明确评分事件，应用与可视星级独立展示。"""
    content = review_content("123", "Demo", review(), updated=updated)
    assert content.startswith(f"**【{title} · 2/5 星】**\n应用：Demo\n")
    assert "评分：★★☆☆☆ 2/5" in content
    assert "购买" not in content


def test_baseline_title_identifies_monitor_activation():
    """启用摘要不冒充新增评分或购买。"""
    content = baseline_content("123", "Demo", 4)
    assert content.startswith("**【评分监控已启用】**\n应用：Demo\n")
    assert "保留期内 4 条评论" in content
    assert "新增评分评论" not in content and "购买" not in content


async def test_expired_delivery_is_not_sent_even_before_periodic_cleanup():
    """投递消费者独立检查保留期，避免过期重试抢先于清理任务发送。"""
    sender = AsyncMock(return_value="123456")
    queue = ReviewDeliveryQueue(None, None, sender, retention_days=30, clock=lambda: 100 * 86400)
    result = await queue._send({"created_at": 69 * 86400, "payload": {"content": "expired"}})
    sender.assert_not_awaited()
    assert result["status"] == "expired" and result["payload"] == {}
    result = await queue._send({"created_at": 70 * 86400, "payload": {"content": "fresh"}})
    sender.assert_awaited_once_with("fresh")
    assert result["status"] == "sent"
