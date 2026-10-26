"""Apple 评论通知文案；完整原文保存在有保留期的数据库中。"""

from datetime import UTC


def _bounded(content: str, units: int) -> str:
    """Discord 按十六位 Unicode 码元计长，截断时不留下半个代理对。"""
    encoded = content.encode("utf-16-le")
    if len(encoded) <= units * 2:
        return content
    return encoded[:(units - 1) * 2].decode("utf-16-le", errors="ignore") + "…"


def review_content(app_id: str, app_name: str, review, *, updated: bool) -> str:
    """保留回复入口和星级；长原文截断，禁止把凭据写入消息。"""
    entry = f"\n回复入口：https://appstoreconnect.apple.com/apps/{app_id}/activity/ratings"
    label = "评论已修改" if updated else "新评论"
    text = (
        f"{app_name} · {label}\n评分：{review.rating}/5\n"
        f"地区：{review.territory} · 用户：{review.reviewer_nickname}\n"
        f"时间：{review.created_at.astimezone(UTC).isoformat(timespec='seconds')}\n"
        f"{review.title}\n{review.body}"
    )
    return _bounded(text, 2000 - len(entry.encode("utf-16-le")) // 2) + entry


def baseline_content(app_id: str, app_name: str, count: int) -> str:
    """首次完整同步只发一条汇总，历史内容不逐条刷屏。"""
    return (
        f"{app_name} · 评论监控已启用\n已建立历史基线：保留期内 {count} 条评论。\n"
        f"后续新增或修改将自动通知。\n"
        f"回复入口：https://appstoreconnect.apple.com/apps/{app_id}/activity/ratings"
    )
