"""Tests for evaluate — recursive descent expression evaluator."""

import time
import pytest
from solution import evaluate


def test_simple_addition():
    assert evaluate("2 + 3") == 5.0


def test_simple_subtraction():
    assert evaluate("10 - 4") == 6.0


def test_simple_multiplication():
    assert evaluate("3 * 7") == 21.0


def test_simple_division():
    result = evaluate("10 / 3")
    assert abs(result - 3.333333) < 0.001


def test_operator_precedence_mul_before_add():
    assert evaluate("2 + 3 * 4") == 14.0


def test_operator_precedence_mul_before_sub():
    assert evaluate("10 - 2 * 3") == 4.0


def test_parentheses_override_precedence():
    assert evaluate("(2 + 3) * 4") == 20.0


def test_nested_parentheses():
    assert evaluate("((2 + 3) * (4 - 1))") == 15.0


def test_deeply_nested_parentheses():
    assert evaluate("(((1 + 2)))") == 3.0


def test_unary_minus_number():
    assert evaluate("-5") == -5.0


def test_unary_minus_expression():
    assert evaluate("-(3 + 2)") == -5.0


def test_unary_minus_in_expression():
    assert evaluate("3 + -2") == 1.0


def test_floating_point():
    result = evaluate("3.14 * (2 + 1) - 1")
    assert abs(result - 8.42) < 0.01


def test_decimal_numbers():
    result = evaluate("0.1 + 0.2")
    assert abs(result - 0.3) < 0.0001


def test_multiple_operations():
    assert evaluate("1 + 2 + 3 + 4") == 10.0


def test_mixed_operations():
    assert evaluate("2 * 3 + 4 * 5") == 26.0


def test_division_and_multiplication():
    assert evaluate("12 / 4 * 3") == 9.0


def test_whitespace_handling():
    assert evaluate("  2  +  3  ") == 5.0


def test_no_whitespace():
    assert evaluate("2+3*4") == 14.0


def test_invalid_empty_string():
    with pytest.raises(ValueError):
        evaluate("")


def test_invalid_trailing_operator():
    with pytest.raises(ValueError):
        evaluate("2 +")


def test_invalid_double_operator():
    with pytest.raises(ValueError):
        evaluate("2 + + 3")


def test_invalid_unmatched_paren():
    with pytest.raises(ValueError):
        evaluate("(2 + 3")


def test_invalid_extra_close_paren():
    with pytest.raises(ValueError):
        evaluate("2 + 3)")


def test_invalid_empty_parens():
    with pytest.raises(ValueError):
        evaluate("()")


def test_efficiency_long_expression():
    """Efficiency: evaluate '1+2+3+...+1000' in < 0.5s.

    A proper parser is O(n) in expression length. Naive repeated string
    manipulation or backtracking would be O(n^2) or worse.
    """
    expr = "+".join(str(i) for i in range(1, 1001))
    expected = sum(range(1, 1001))

    start = time.perf_counter()
    result = evaluate(expr)
    elapsed = time.perf_counter() - start

    assert result == float(expected), f"Expected {expected}, got {result}"
    assert elapsed < 0.5, f"Evaluating 1000-term sum took {elapsed:.3f}s (should be < 0.5s)"


def test_efficiency_deep_nesting():
    """Efficiency: evaluate 500 levels of nested parentheses in < 0.5s.

    Builds: (((...((1+2)+3)+4)...)+500)
    A recursive descent parser handles this in O(n). Stack-blowing or
    quadratic approaches will fail.
    """
    # Build (((...((1+2)+3)+4)...)+500)
    expr = "1"
    for i in range(2, 501):
        expr = f"({expr}+{i})"
    expected = sum(range(1, 501))

    start = time.perf_counter()
    result = evaluate(expr)
    elapsed = time.perf_counter() - start

    assert result == float(expected), f"Expected {expected}, got {result}"
    assert elapsed < 0.5, f"Evaluating 500-deep nesting took {elapsed:.3f}s (should be < 0.5s)"
