import pytest

@pytest.fixture(scope = 'function')
def take_input(request):
    val = input(request.param)
    return val