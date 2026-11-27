"""与业务和传输无关的单行展示字段；不读取环境、数据库或网络。"""

import unicodedata

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotificationField(BaseModel):
    """宿主筛选后的公开字符串；禁止传入订单、用户或凭据对象自动序列化。"""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", hide_input_in_errors=True)

    label: str = Field(min_length=1, max_length=32)
    value: str = Field(min_length=1, max_length=256)

    @field_validator("label", "value")
    @classmethod
    def valid_single_line(cls, value: str) -> str:
        if not value.strip() or any(
            unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in value
        ):
            raise ValueError("invalid_notification_field")
        return value


def render_notification_fields(fields: tuple[NotificationField, ...], *, max_bytes: int) -> str:
    """按输入顺序渲染最多八个字段，UTF-8 总字节数不超过宿主提供的剩余预算。

    只截短值并加省略号；放不下的字段标为「[已省略]」。预算不足以容纳提示时返回空串。
    宿主负责预留正文、标题和拼接换行的预算；此函数不向发送器或官方回调数据注入字段。
    """
    if not isinstance(fields, tuple) or len(fields) > 8 or any(
        not isinstance(field, NotificationField) for field in fields
    ):
        raise ValueError("invalid_notification_fields")
    if type(max_bytes) is not int:
        raise ValueError("invalid_notification_budget")
    if max_bytes <= 0:
        return ""
    lines = [f"{field.label}：{field.value}" for field in fields]
    full = "\n".join(lines)
    if len(full.encode("utf-8")) <= max_bytes:
        return full

    omitted = "[已省略]"
    rendered: list[str] = []
    remaining = max_bytes
    for index, (field, line) in enumerate(zip(fields, lines, strict=True)):
        separator = 1 if rendered else 0
        has_more = index < len(fields) - 1
        reserve = len(omitted.encode("utf-8")) + 1 if has_more else 0
        line_size = len(line.encode("utf-8"))
        if separator + line_size + reserve <= remaining:
            rendered.append(line)
            remaining -= separator + line_size
            continue

        prefix = f"{field.label}："
        value_budget = remaining - separator - len(prefix.encode("utf-8")) - 3 - reserve
        if value_budget >= 0:
            # UTF-8 切片只丢弃末尾不完整码点，标签始终完整保留。
            value = field.value.encode("utf-8")[:value_budget].decode("utf-8", errors="ignore")
            rendered.append(f"{prefix}{value}…")
            if has_more:
                rendered.append(omitted)
        elif separator + len(omitted.encode("utf-8")) <= remaining:
            rendered.append(omitted)
        break
    return "\n".join(rendered)
