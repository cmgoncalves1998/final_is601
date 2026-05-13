from typing import Union

import pytest

from app.operations import add, divide, multiply, subtract


Number = Union[int, float]


@pytest.mark.parametrize(
    "a, b, exp",
    [
        (2, 3, 5),
        (-2, -3, -5),
        (2.5, 3.5, 6.0),
        (-2.5, 3.5, 1.0),
        (0, 0, 0),
    ],
    ids=["pos_int", "neg_int", "pos_float", "mix_float", "zero"],
)
def test_add(a: Number, b: Number, exp: Number) -> None:
    res = add(a, b)
    assert res == exp, f"add({a}, {b}) -> {res}, exp {exp}"


@pytest.mark.parametrize(
    "a, b, exp",
    [
        (5, 3, 2),
        (-5, -3, -2),
        (5.5, 2.5, 3.0),
        (-5.5, -2.5, -3.0),
        (0, 0, 0),
    ],
    ids=["pos_int", "neg_int", "pos_float", "neg_float", "zero"],
)
def test_sub(a: Number, b: Number, exp: Number) -> None:
    res = subtract(a, b)
    assert res == exp, f"sub({a}, {b}) -> {res}, exp {exp}"


@pytest.mark.parametrize(
    "a, b, exp",
    [
        (2, 3, 6),
        (-2, 3, -6),
        (2.5, 4.0, 10.0),
        (-2.5, 4.0, -10.0),
        (0, 5, 0),
    ],
    ids=["pos_int", "mix_int", "pos_float", "mix_float", "zero"],
)
def test_mul(a: Number, b: Number, exp: Number) -> None:
    res = multiply(a, b)
    assert res == exp, f"mul({a}, {b}) -> {res}, exp {exp}"


@pytest.mark.parametrize(
    "a, b, exp",
    [
        (6, 3, 2.0),
        (-6, 3, -2.0),
        (6.0, 3.0, 2.0),
        (-6.0, 3.0, -2.0),
        (0, 5, 0.0),
    ],
    ids=["pos_int", "mix_int", "pos_float", "mix_float", "zero"],
)
def test_div(a: Number, b: Number, exp: float) -> None:
    res = divide(a, b)
    assert res == exp, f"div({a}, {b}) -> {res}, exp {exp}"


def test_div_zero() -> None:
    with pytest.raises(ValueError) as exc:
        divide(6, 0)

    assert "Cannot divide by zero!" in str(exc.value)
