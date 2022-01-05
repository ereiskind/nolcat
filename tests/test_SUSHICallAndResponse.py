import pytest

from nolcat.SUSHI_call_and_response import SUSHICallAndResponse

"""
For testing the SUSHI API, a fixture that prompts the user for the SUSHI API information in stdout is applied to all the tests requiring data to make API calls. This semi-automated method, which collects a valid SUSHI URL and set of credentials from the user and applies them to all tests, is used because:
    1. There is no set of testing credentials; even using the SwaggerHub testing service requires SUSHI credentials from a vendor.
    2. SUSHI credentials are unique to each institution and should be secret, so using the API would require another secure file or a mechanism to randomly select a set of SUSHI credentials from whereever they're being stored.
    3. The JSON formatting used for the API responses contains some inconsistencies among vendors, so the ability to control which vendor is being used for testing is valuable.
"""


@pytest.fixture(scope='session')  # Without the scope, the data prompts appear in stdout for each test
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

    return (URL, SUSHI_credentials)


def test_input1(take_input1):
    # The test starts by going to the fixture `take_input1`
    # Whatever is entered into stdin is returned to the test as the value of the parameter variable `take_input1`
    print(f"The value of take_input1 is {take_input1}")
    assert True


def test_input1_again(take_input1):
    # The test starts by going to the fixture `take_input1`
    # Whatever is entered into stdin is returned to the test as the value of the parameter variable `take_input1`
    print(f"The value of take_input1 in second test is {take_input1}")
    assert True