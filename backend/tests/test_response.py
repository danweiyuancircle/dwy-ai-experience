"""Tests for dwyeapi.response (ApiResponse + PageData)."""

from pydantic import BaseModel

from dwyeapi.response import ApiResponse, PageData


class _Item(BaseModel):
    id: int
    name: str


class TestApiResponseOk:
    def test_default_message_and_code(self):
        resp = ApiResponse.ok(data={"id": 1})
        assert resp.code == "SUCCESS"
        assert resp.message == "success"
        assert resp.data == {"id": 1}
        assert isinstance(resp.timestamp, int)

    def test_custom_message(self):
        resp = ApiResponse.ok(data=None, message="created")
        assert resp.message == "created"
        assert resp.code == "SUCCESS"

    def test_data_can_be_none(self):
        resp = ApiResponse.ok(data=None)
        assert resp.data is None

    def test_data_is_pydantic_model(self):
        item = _Item(id=1, name="alice")
        resp = ApiResponse.ok(data=item)
        assert resp.data is item
        dumped = resp.model_dump()
        assert dumped["data"] == {"id": 1, "name": "alice"}

    def test_serialization_shape(self):
        resp = ApiResponse.ok(data={"id": 1})
        dumped = resp.model_dump()
        assert set(dumped.keys()) == {"code", "message", "data", "timestamp"}
        assert dumped["code"] == "SUCCESS"


class TestApiResponsePage:
    def test_page_structure(self):
        items = [_Item(id=1, name="a"), _Item(id=2, name="b")]
        resp = ApiResponse.page(items=items, total=50, page=1, page_size=20)
        assert resp.code == "SUCCESS"
        assert resp.message == "success"
        assert isinstance(resp.data, PageData)
        assert resp.data.items == items
        assert resp.data.total == 50
        assert resp.data.page == 1
        assert resp.data.page_size == 20

    def test_page_serialization(self):
        items = [_Item(id=1, name="a")]
        resp = ApiResponse.page(items=items, total=1, page=1, page_size=20)
        dumped = resp.model_dump()
        assert dumped["data"] == {
            "items": [{"id": 1, "name": "a"}],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }

    def test_empty_page(self):
        resp = ApiResponse.page(items=[], total=0, page=1, page_size=20)
        assert resp.data.items == []
        assert resp.data.total == 0

    def test_custom_message_on_page(self):
        resp = ApiResponse.page(items=[], total=0, page=1, page_size=20, message="empty")
        assert resp.message == "empty"


class TestApiResponseDirectConstruction:
    """错误态 handler 会直接实例化 ApiResponse(code=业务错误码, ...) — 必须支持。"""

    def test_construct_with_custom_code(self):
        resp = ApiResponse(code="NOT_FOUND", message="用户不存在", data=None)
        assert resp.code == "NOT_FOUND"
        assert resp.message == "用户不存在"
        assert resp.data is None
        assert isinstance(resp.timestamp, int)

    def test_serialize_error_shape(self):
        resp = ApiResponse(code="INSUFFICIENT_BALANCE", message="余额不足", data=None)
        dumped = resp.model_dump()
        assert dumped == {
            "code": "INSUFFICIENT_BALANCE",
            "message": "余额不足",
            "data": None,
            "timestamp": dumped["timestamp"],
        }


class TestPageData:
    def test_standalone_construction(self):
        page = PageData[_Item](items=[_Item(id=1, name="x")], total=1, page=1, page_size=10)
        assert page.total == 1
        assert page.items[0].id == 1

    def test_from_attributes(self):
        class _Row:
            def __init__(self):
                self.items = [_Item(id=1, name="x")]
                self.total = 1
                self.page = 1
                self.page_size = 10

        page = PageData[_Item].model_validate(_Row())
        assert page.total == 1
