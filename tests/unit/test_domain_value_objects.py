import pytest

from app.domain.value_objects import BoundedText, DomainValidationError, Email, WatchedPercentage


def test_bounded_text_valid():
    t = BoundedText("hello", 1, 10)
    assert t.value == "hello"


@pytest.mark.parametrize(
    "value,min_len,max_len",
    [
        ("", 1, 10),
        ("toolong", 1, 3),
    ],
)
def test_bounded_text_invalid(value, min_len, max_len):
    with pytest.raises(DomainValidationError):
        BoundedText(value, min_len, max_len)


def test_email_invalid():
    with pytest.raises(DomainValidationError):
        Email("no-at-symbol")


@pytest.mark.parametrize("v", [-0.1, 1.1])
def test_watched_percentage_out_of_range(v):
    with pytest.raises(DomainValidationError):
        WatchedPercentage(v)
