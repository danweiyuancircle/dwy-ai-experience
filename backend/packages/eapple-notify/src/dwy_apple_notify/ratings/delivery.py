"""评分汇总的名单撤销边界，租约和重试继续复用通用队列。"""

from collections.abc import Collection

from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue


class RatingDeliveryQueue(SQLAlchemyDeliveryQueue):
    """日报任一应用被撤销时停止整份投递，避免历史固定内容绕过当前名单。"""

    def __init__(self, sessions, table, sender=None, *, app_ids: Collection[str], **options):
        """名单来自当前监控配置；时区变化不撤销应用，也不重写历史日报。"""
        super().__init__(sessions, table, sender, source="app_store_ratings", **options)
        self.app_ids = frozenset(app_ids)

    async def _send(self, row) -> dict:
        if not set(row["payload"]["app_ids"]).issubset(self.app_ids):
            return {"status": "suppressed", "payload": {}, "error_code": None}
        return await super()._send(row)
