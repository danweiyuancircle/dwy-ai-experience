"""精确日期对比与固定日报文本；不将累计均分差解释为新增评分。"""

import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo


def comparison_dates(day: date) -> dict[str, date]:
    """日/周取精确日期；月取上月同日并按当月天数截断。"""
    previous_month = day.replace(day=1) - timedelta(days=1)
    monthly = previous_month.replace(
        day=min(
            day.day,
            calendar.monthrange(
                previous_month.year,
                previous_month.month,
            )[1],
        )
    )
    return {"日": day - timedelta(days=1), "周": day - timedelta(days=7), "月": monthly}


def digest_content(
    config, day: date, collected_at: int, current: dict, history: dict, seen_scopes: set[tuple[str, str]]
) -> str:
    """所有应用和地区归入一份日报；缺日不借用最近快照，不把失败写成零。"""
    actual = datetime.fromtimestamp(collected_at, ZoneInfo(config.timezone))
    parts = [
        f"每日评分日报 · {day.isoformat()}",
        f"实际采集时间：{actual.isoformat(timespec='seconds')}（{config.timezone}）",
    ]
    if actual.date() > day:
        parts.append("采集跨日，本轮数据不可用。")
    for app_id, application in config.apps.items():
        for territory in config.territories:
            parts.append(f"\n{application.name} · {territory}")
            value = current[(app_id, territory)]
            if value is None:
                parts.append("数据暂不可用；未使用旧值或零值替代今日评分。")
                continue
            parts.append(f"当前评分总数：{value.count}，平均评分：{value.average:.2f}")
            if (app_id, territory) not in seen_scopes:
                parts.append("首次采集，暂无对比。")
            for label, baseline_day in comparison_dates(day).items():
                baseline = history.get((app_id, territory, baseline_day.isoformat()))
                reference = f"（对比 {baseline_day.isoformat()}）"
                if baseline is None:
                    parts.append(f"{label}变化：暂无历史数据{reference}")
                    continue
                if baseline["status"] != "ok":
                    parts.append(f"{label}变化：基准日采集失败{reference}")
                    continue
                difference = Decimal(str(value.average)) - Decimal(str(baseline["average"]))
                average = f"{difference:+.2f}"
                if difference != 0 and difference.quantize(Decimal("0.01")) == 0:
                    average = "变化小于显示精度"
                parts.append(
                    f"{label}变化：评分数净变化 {value.count - baseline['count']:+d}，"
                    f"均分 {average}{reference}"
                )
    parts.append(
        "\n统计口径：各地区全部评分，含仅打星和文字评价附带的星级；"
        "均分变化为累计均分之差，不能识别每次仅打星评分。"
    )
    return "\n".join(parts)


def split_content(content: str) -> list[str]:
    """无损分段，按 Discord 的 2000 UTF-16 单位限制保留完整日报。"""
    chunks, start, units = [], 0, 0
    for index, character in enumerate(content):
        size = 2 if ord(character) > 0xFFFF else 1
        if units + size > 2000:
            chunks.append(content[start:index])
            start, units = index, 0
        units += size
    if start < len(content):
        chunks.append(content[start:])
    return chunks
