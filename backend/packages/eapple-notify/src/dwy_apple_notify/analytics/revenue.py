"""Apple 购买报表的完整 UTC 周期及金额展示。"""

from datetime import date, timedelta
from decimal import Decimal

from .formatting import _bounded
from .models import AppleBusinessSnapshot

_METRICS = ("sales_usd", "refunds_usd", "proceeds_usd")
_LABELS = ("销售额（退款前）", "退款额", "开发者预估净收益")
_DAY = timedelta(days=1)
_WEEK = timedelta(days=7)


def revenue_periods(today: date):
    """按 Apple 发布日返回最新可用期间、前一期起点和应发布日期。"""
    monday = today - timedelta(days=(today.weekday() - 4) % 7 + 4)
    month = (today - timedelta(days=4)).replace(day=1)
    previous_month = (month - _DAY).replace(day=1)
    yield "weekly", monday - _WEEK, monday - _DAY, monday - 2 * _WEEK, monday + 4 * _DAY
    yield "monthly", previous_month, month - _DAY, (previous_month - _DAY).replace(day=1), month + 4 * _DAY


def revenue_amounts(snapshot: AppleBusinessSnapshot) -> tuple[Decimal, Decimal, Decimal] | None:
    """缺少任何金额时返回 None；退款不得在净收益中重复扣除。"""
    metrics = [snapshot.metrics.get(key) for key in _METRICS]
    if any(v is None or v.status != "available" or v.currency != "USD" or v.value is None for v in metrics):
        return None
    net_sales, refunds, proceeds = (v.value for v in metrics)
    return net_sales + refunds, refunds, proceeds


def revenue_content(period, start, end, apps, current, previous) -> list[str]:
    """汇总各 App 的三个金额，只在全部 App 数据齐全时输出合计。"""
    title = f"**【Apple 收入{'周报' if period == 'weekly' else '月报'}】**"
    header = f"{title}\n{start} 至 {end}（UTC）｜USD"

    def line(name, values, comparison):
        if values is None:
            return f"**{name}**｜数据未提供"
        fields = []
        for index, (label, value) in enumerate(zip(_LABELS, values, strict=True)):
            change = f"（较上期 {value - comparison[index]:+,.2f}）" if comparison is not None else ""
            fields.append(f"{label} {value:,.2f}{change}")
        return f"**{name}**｜" + " · ".join(fields)

    def total(values):
        if any(value is None for value in values.values()):
            return None
        return tuple(sum(column, Decimal(0)) for column in zip(*values.values(), strict=True))

    parts = [header + "\n" + line("合计", total(current), total(previous))]
    for app_id, app in apps.items():
        row = line(_bounded(app.name, 128), current[app_id], previous[app_id])
        if len((parts[-1] + "\n" + row).encode("utf-16-le")) // 2 > 2000:
            parts.append(header)
        parts[-1] += "\n" + row
    return parts
