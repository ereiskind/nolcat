import pytest

@pytest.fixture(scope = 'function')
def take_input2(request):
    val = input(request.param)
    return val
