"""Tests for chat candidate pre-filtering helpers."""
from __future__ import annotations

import pytest

from app.api.v1.chat import _primary_category_for_query


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("给我 3 个美区家居爆品", "Home"),
        ("厨房小工具里单价 15 美金左右、复购率高的品", "Kitchen"),
        ("宠物类、增速最快的品", "Pet"),
        ("美妆个护里近期 GMV 飙升的品", "Beauty"),
        ("户外露营适合短视频展示的品", "Outdoor"),
        ("儿童玩具里适合达人带货的品", "Kids"),
        ("数码周边里低客单价高增长的品", "Tech"),
        ("home storage products under 30 dollars", "Home"),
        ("pet grooming products with creator momentum", "Pet"),
        ("随便给我 3 个爆品", None),
    ],
)
def test_primary_category_for_query(query: str, expected: str | None):
    assert _primary_category_for_query(query) == expected


def test_primary_category_uses_earliest_explicit_match():
    assert _primary_category_for_query("家居小工具，不要厨房用品") == "Home"
