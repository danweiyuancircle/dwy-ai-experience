"""Tests for danweiyuan_base.pagination."""

import pytest

from danweiyuan_base.pagination import OffsetLimit, PaginationParams, paginate


class TestPaginate:
    def test_first_page(self):
        assert paginate(1, 20) == OffsetLimit(offset=0, limit=20)

    def test_third_page(self):
        assert paginate(3, 10) == OffsetLimit(offset=20, limit=10)

    def test_page_zero_treated_as_one(self):
        assert paginate(0, 20) == OffsetLimit(offset=0, limit=20)

    def test_negative_page_treated_as_one(self):
        assert paginate(-5, 20) == OffsetLimit(offset=0, limit=20)


class TestPaginationParams:
    def test_defaults(self):
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_custom_values(self):
        params = PaginationParams(page=3, page_size=50)
        assert params.page == 3

    def test_page_min_is_one(self):
        with pytest.raises(ValueError):
            PaginationParams(page=0)

    def test_page_size_max_is_100(self):
        with pytest.raises(ValueError):
            PaginationParams(page_size=101)
