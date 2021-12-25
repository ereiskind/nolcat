import pytest

from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

@pytest.fixture(scope = 'function')
def take_input1(request):
    val = input(request.param)
    return val

@pytest.mark.parametrize('take_input1', ('Enter value 1 here:'), indirect = True)
def test_input1(take_input1):
    print(f"The value of take_input1 is {take_input1}")
    assert True

@pytest.mark.parametrize('take_input2', ('Enter value 2 here:'), indirect = True)
def test_input2(take_input2):
    print(f"The value of take_input2 is {take_input2}")
    assert True

'''@pytest.fixture
def SUSHI_credentials_fixture():
    """A fixture to collect and store the data for making SUSHI calls."""
    URL = input("Enter the SUSHI base URL, including the final backslash: ")
    user_id = input("Enter the SUSHI customer ID: ")
    requestor_id = input("Enter the SUSHI requestor ID or just press enter if none exists: ")
    api_key = input("Enter the SUSHI API key or just press enter if none exists: ")
    platform = input("Enter the SUSHI platform or just press enter if none exists: ")

    SUSHI_credentials = dict(user_id = user_id)
    if requestor_id != "":
        SUSHI_credentials['requestor_id'] = requestor_id
    if api_key != "":
        SUSHI_credentials['api_key'] = api_key
    if platform != "":
        SUSHI_credentials['platform'] = platform
    
    print(URL)
    print(SUSHI_credentials)

    yield (URL, SUSHI_credentials)'''