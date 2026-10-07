import datetime

import pytest

import pricing


@pytest.fixture(autouse=True)
def reset_pricing_state():
    pricing.member_points.clear()
    pricing.LOG.clear()


def test_regular_price_without_benefits():
    assert pricing.calc([("item", 2, 10)]) == 21.4


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [
        (50, 50.83),
        (100, 96.3),
    ],
)
def test_bulk_discount_at_each_threshold(quantity, expected):
    assert pricing.calc([("item", quantity, 1)]) == expected


def test_zero_quantity_is_ignored():
    assert pricing.calc([("item", 0, 10)]) == 0


def test_member_discount_and_points():
    assert pricing.calc([("item", 10, 20)], member="member-1") == 203.3
    assert pricing.member_points["member-1"] == 1


@pytest.mark.parametrize(
    ("coupon", "today", "expected"),
    [
        ("SAVE50", None, 160.5),
        ("HALF", None, 107),
        ("NEWYEAR", datetime.date(2026, 1, 15), 171.2),
        ("NEWYEAR", datetime.date(2026, 2, 15), 214),
    ],
)
def test_known_coupons(coupon, today, expected):
    assert pricing.calc([("item", 10, 20)], coupon=coupon, today=today) == expected


def test_amount_below_fixed_coupon_discount_is_clamped_to_zero():
    assert pricing.calc([("item", 1, 40)], coupon="SAVE50") == 0


def test_log_records_member_and_final_amount_for_every_call():
    first = pricing.calc([("item", 1, 10)])
    second = pricing.calc([("item", 2, 10)], member="member-1")

    assert pricing.LOG == [(None, first), ("member-1", second)]
