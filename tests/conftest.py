import pytest
import asyncio

# Configure pytest-asyncio to use "auto" mode
pytest.register_assert_rewrite('pytest_asyncio')

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as requiring asyncio"
    ) 