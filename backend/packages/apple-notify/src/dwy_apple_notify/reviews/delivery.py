"""评论来源独有的过期投递边界；通用队列继续负责租约和退避。"""

from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue


class ReviewDeliveryQueue(SQLAlchemyDeliveryQueue):
    """已过评论保留期的消息不再发送，周期清理前也不能继续重试。"""

    def __init__(self, sessions, table, sender=None, *, retention_days: int, **options):
        """保留期限由同一采集配置注入，不读取宿主全局配置。"""
        super().__init__(sessions, table, sender, source="app_store_reviews", **options)
        self.retention_days = retention_days

    async def _send(self, row) -> dict:
        """发送前复核期限；网络请求一旦开始，其接收行为由通知平台决定。"""
        if row["created_at"] < int(self.clock()) - self.retention_days * 86400:
            return {"status": "expired", "payload": {}, "error_code": None}
        return await super()._send(row)
