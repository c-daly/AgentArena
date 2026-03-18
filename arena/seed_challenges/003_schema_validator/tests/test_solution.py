"""Tests for validate — recursive JSON schema validator."""

import time
from solution import validate


# --- Primitive types ---

def test_int_valid():
    assert validate(42, {"type": "int"}) is True


def test_int_invalid():
    assert validate("42", {"type": "int"}) is False


def test_str_valid():
    assert validate("hello", {"type": "str"}) is True


def test_str_invalid():
    assert validate(42, {"type": "str"}) is False


def test_float_valid():
    assert validate(3.14, {"type": "float"}) is True


def test_float_accepts_int():
    """int is a subtype of float in practice."""
    assert validate(42, {"type": "float"}) is True


def test_float_invalid():
    assert validate("3.14", {"type": "float"}) is False


def test_bool_valid():
    assert validate(True, {"type": "bool"}) is True
    assert validate(False, {"type": "bool"}) is True


def test_bool_invalid():
    assert validate(1, {"type": "bool"}) is False


def test_any_accepts_anything():
    assert validate(42, {"type": "any"}) is True
    assert validate("hello", {"type": "any"}) is True
    assert validate([1, 2], {"type": "any"}) is True
    assert validate(None, {"type": "any"}) is True
    assert validate({"a": 1}, {"type": "any"}) is True


# --- List validation ---

def test_list_valid():
    assert validate([1, 2, 3], {"type": "list", "items": {"type": "int"}}) is True


def test_list_empty():
    assert validate([], {"type": "list", "items": {"type": "int"}}) is True


def test_list_invalid_item():
    assert validate([1, "two", 3], {"type": "list", "items": {"type": "int"}}) is False


def test_list_not_a_list():
    assert validate("not a list", {"type": "list", "items": {"type": "int"}}) is False


# --- Dict validation ---

def test_dict_valid():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "age": {"type": "int"},
        },
    }
    assert validate({"name": "Alice", "age": 30}, schema) is True


def test_dict_missing_required_field():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "age": {"type": "int"},
        },
    }
    assert validate({"name": "Alice"}, schema) is False


def test_dict_wrong_field_type():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "age": {"type": "int"},
        },
    }
    assert validate({"name": "Alice", "age": "thirty"}, schema) is False


def test_dict_not_a_dict():
    schema = {"type": "dict", "fields": {"x": {"type": "int"}}}
    assert validate([1, 2], schema) is False


def test_dict_optional_field_present():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "email": {"type": "str"},
        },
        "optional": ["email"],
    }
    assert validate({"name": "Alice", "email": "a@b.com"}, schema) is True


def test_dict_optional_field_absent():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "email": {"type": "str"},
        },
        "optional": ["email"],
    }
    assert validate({"name": "Alice"}, schema) is True


def test_dict_optional_field_wrong_type():
    schema = {
        "type": "dict",
        "fields": {
            "name": {"type": "str"},
            "email": {"type": "str"},
        },
        "optional": ["email"],
    }
    assert validate({"name": "Alice", "email": 123}, schema) is False


# --- Union types ---

def test_union_first_matches():
    schema = {"type": "union", "options": [{"type": "int"}, {"type": "str"}]}
    assert validate(42, schema) is True


def test_union_second_matches():
    schema = {"type": "union", "options": [{"type": "int"}, {"type": "str"}]}
    assert validate("hello", schema) is True


def test_union_none_matches():
    schema = {"type": "union", "options": [{"type": "int"}, {"type": "str"}]}
    assert validate([1, 2], schema) is False


# --- Nested structures ---

def test_nested_dict_in_dict():
    schema = {
        "type": "dict",
        "fields": {
            "user": {
                "type": "dict",
                "fields": {
                    "name": {"type": "str"},
                    "age": {"type": "int"},
                },
            },
        },
    }
    assert validate({"user": {"name": "Alice", "age": 30}}, schema) is True
    assert validate({"user": {"name": "Alice", "age": "old"}}, schema) is False


def test_list_of_dicts():
    schema = {
        "type": "list",
        "items": {
            "type": "dict",
            "fields": {
                "id": {"type": "int"},
                "value": {"type": "str"},
            },
        },
    }
    data = [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}]
    assert validate(data, schema) is True

    bad_data = [{"id": 1, "value": "a"}, {"id": "two", "value": "b"}]
    assert validate(bad_data, schema) is False


def test_union_with_complex_types():
    schema = {
        "type": "union",
        "options": [
            {"type": "list", "items": {"type": "int"}},
            {"type": "dict", "fields": {"x": {"type": "int"}}},
        ],
    }
    assert validate([1, 2, 3], schema) is True
    assert validate({"x": 5}, schema) is True
    assert validate("neither", schema) is False


# --- Efficiency benchmarks ---

def test_efficiency_deep_nesting():
    """Efficiency: validate a 100-level nested dict->list->dict structure in < 0.5s.

    A proper recursive validator is O(n) in schema/data size. Quadratic
    approaches (e.g., re-traversing the schema for each level) will fail.
    """
    # Build schema: dict -> list -> dict -> list -> ... (100 levels)
    inner_schema = {"type": "int"}
    inner_data = 42
    for i in range(100):
        if i % 2 == 0:
            inner_schema = {
                "type": "dict",
                "fields": {"val": inner_schema},
            }
            inner_data = {"val": inner_data}
        else:
            inner_schema = {"type": "list", "items": inner_schema}
            inner_data = [inner_data]

    start = time.perf_counter()
    result = validate(inner_data, inner_schema)
    elapsed = time.perf_counter() - start

    assert result is True, "Deep nested validation should pass"
    assert elapsed < 0.5, f"100-level deep validation took {elapsed:.3f}s (should be < 0.5s)"


def test_efficiency_large_list():
    """Efficiency: validate a list of 10000 items in < 0.5s.

    Linear scan is required — O(n^2) approaches will timeout.
    """
    schema = {
        "type": "list",
        "items": {
            "type": "dict",
            "fields": {
                "id": {"type": "int"},
                "name": {"type": "str"},
                "active": {"type": "bool"},
            },
        },
    }
    data = [{"id": i, "name": f"item_{i}", "active": i % 2 == 0} for i in range(10000)]

    start = time.perf_counter()
    result = validate(data, schema)
    elapsed = time.perf_counter() - start

    assert result is True, "Large list validation should pass"
    assert elapsed < 0.5, f"10000-item list validation took {elapsed:.3f}s (should be < 0.5s)"
