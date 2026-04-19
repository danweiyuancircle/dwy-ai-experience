"""Tests for dwyeapi.response."""

from dwyeapi.response import fail, paginated, success


class TestSuccess:
    def test_default_message(self):
        result = success(data={"id": 1})
        assert result["code"] == 200
        assert result["message"] == "success"
        assert result["data"] == {"id": 1}
        assert "timestamp" in result

    def test_custom_message(self):
        result = success(data=None, message="created")
        assert result["message"] == "created"

    def test_no_data(self):
        result = success()
        assert result["data"] is None


class TestFail:
    def test_default_values(self):
        result = fail()
        assert result["code"] == 400
        assert result["message"] == "fail"

    def test_custom_code_and_message(self):
        result = fail(code=500, message="internal error")
        assert result["code"] == 500


class TestPaginated:
    def test_paginated_structure(self):
        items = [{"id": 1}, {"id": 2}]
        result = paginated(items=items, total=50, page=1, page_size=20)
        assert result["code"] == 200
        data = result["data"]
        assert data["items"] == items
        assert data["total"] == 50
        assert data["page"] == 1
        assert data["page_size"] == 20
