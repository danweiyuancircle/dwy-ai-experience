"""公开展示字段只接收已筛选的字符串，按 UTF-8 剩余预算渲染。"""

import pytest
import requests
from pydantic import ValidationError

from dwy_notify import (
    NotificationAppearance,
    NotificationConfig,
    NotificationField,
    Notifier,
    render_notification_fields,
)


def test_fields_preserve_order_and_never_mutate_the_input():
    fields = (NotificationField(label="用户", value="小明"), NotificationField(label="Order", value="A-1"))
    assert render_notification_fields(fields, max_bytes=100) == "用户：小明\nOrder：A-1"
    assert render_notification_fields((), max_bytes=100) == ""
    with pytest.raises(ValidationError, match="frozen_instance"):
        fields[0].value = "changed"


@pytest.mark.parametrize("name,limit", [("label", 32), ("value", 256)])
def test_field_length_boundaries_and_strict_strings(name, limit):
    values = {"label": "标签", "value": "内容"}
    values[name] = "x"
    assert getattr(NotificationField(**values), name) == "x"
    values[name] = "中" * limit
    assert getattr(NotificationField(**values), name) == values[name]
    for invalid in ("", "x" * (limit + 1), 1, True, b"bytes", {"private": "object"}, object()):
        values[name] = invalid
        with pytest.raises(ValidationError):
            NotificationField(**values)


@pytest.mark.parametrize("name", ["label", "value"])
@pytest.mark.parametrize("character", [
    "\n", "\r", "\t", "\x00", "\x7f", "\x85", "\u200d", "\u2028", "\u2029", "\u202e", "\ud800",
])
def test_fields_reject_controls_and_line_separators(name, character):
    values = {"label": "标签", "value": "内容"}
    values[name] = "private" + character
    with pytest.raises(ValidationError) as error:
        NotificationField(**values)
    assert "private" not in str(error.value)


def test_fields_reject_blank_and_unexpected_properties_without_echoing_input():
    with pytest.raises(ValidationError) as error:
        NotificationField(label=" ", value="private-value", token="private-token")
    assert "private-value" not in str(error.value)
    assert "private-token" not in str(error.value)


def test_field_count_and_input_contract():
    field = NotificationField(label="标签", value="值")
    assert len(render_notification_fields((field,) * 8, max_bytes=1000).splitlines()) == 8
    with pytest.raises(ValueError, match="invalid_notification_fields"):
        render_notification_fields((field,) * 9, max_bytes=1000)
    with pytest.raises(ValueError, match="invalid_notification_fields"):
        render_notification_fields(({"label": "a", "value": "b"},), max_bytes=1000)
    for invalid in (True, 1.0, "100"):
        with pytest.raises(ValueError, match="invalid_notification_budget"):
            render_notification_fields((field,), max_bytes=invalid)


@pytest.mark.parametrize("value", ["abcdefghijklmnopqrstuvwxyz", "中文展示字段" * 20, "汉字🙂é" * 40])
def test_every_utf8_budget_preserves_complete_labels_and_marks_truncation(value):
    field = NotificationField(label="名称", value=value)
    full = "名称：" + value
    for budget in range(len(full.encode()) + 2):
        rendered = render_notification_fields((field,), max_bytes=budget)
        assert len(rendered.encode()) <= budget
        assert rendered.encode().decode() == rendered
        if rendered.startswith("名称："):
            if rendered != full:
                assert rendered.endswith("…")
                assert value.startswith(rendered.removeprefix("名称：").removesuffix("…"))
        else:
            assert rendered in ("", "[已省略]")
    assert render_notification_fields((field,), max_bytes=len(full.encode())) == full


def test_missing_fields_have_an_explicit_marker_and_no_partial_labels():
    fields = tuple(NotificationField(label=f"字段{i}", value="a" * 100) for i in range(8))
    full = "\n".join(f"{field.label}：{field.value}" for field in fields)
    for budget in range(len(full.encode()) + 1):
        rendered = render_notification_fields(fields, max_bytes=budget)
        assert len(rendered.encode()) <= budget
        lines = rendered.splitlines()
        visible = [line for line in lines if line != "[已省略]"]
        assert all(line.startswith(f"字段{i}：") for i, line in enumerate(visible))
        if rendered and len(visible) < len(fields):
            assert lines[-1] == "[已省略]"
        if rendered and len(visible) == len(fields) and rendered != full:
            assert lines[-1].endswith("…")


@pytest.mark.parametrize("budget", [-100, -1, 0, 1, 2, 3, 10])
def test_tiny_or_exhausted_budget_is_safe(budget):
    fields = (NotificationField(label="标签", value="内容"),)
    assert render_notification_fields(fields, max_bytes=budget) == ""


async def test_wecom_text_keeps_markdown_and_mentions_as_plain_content(monkeypatch):
    fields = (NotificationField(label="*订单*", value="@all <@123> **内容**"),)
    content = render_notification_fields(fields, max_bytes=100)
    payloads = []

    def post(url, **kwargs):
        payloads.append(kwargs["json"])
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"errcode": 0}'
        return response

    monkeypatch.setattr("dwy_notify._transport.post", post)
    notifier = Notifier(NotificationConfig(
        targets={"ops": "wecombot://offline-key"}, appearance=NotificationAppearance(username="通知"),
    ))
    assert (await notifier.send(content)).success
    assert payloads == [{"msgtype": "text", "text": {"content": "*订单*：@all <@123> **内容**"}}]
