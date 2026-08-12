import pytest

from validators import validate_text


@pytest.mark.parametrize("value", ["123", "Abcd", "12345", "abcdef"])
def test_validate_text_for_valid_length(value):
    assert validate_text(value, "欄位", 3, 6) is None


@pytest.mark.parametrize("value", ["", "ab", "1234567"])
def test_validate_text_for_invalid_length(value: str):
    assert validate_text(value, "欄位", 3, 6) is not None


@pytest.mark.parametrize("value", ["a b", "123 45", " 12", "abcde "])
def test_validate_text_when_value_contains_whitespace(value):
    assert validate_text(value, "欄位", 3, 6) is not None