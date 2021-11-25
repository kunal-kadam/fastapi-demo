import pytest

@pytest.mark.parametrize("num1, num2, expected", [
    (3, 2, 5),
    (7, 2, 9),
    (12, 4, 16)
])
def test_add(num1, num2, expected):
    # print("Testing add function")
    assert num1 + num2 == expected

