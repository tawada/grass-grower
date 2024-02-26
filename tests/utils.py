"""Utility functions for testing."""


class MockFile:
    """Mock file class."""

    def __init__(self, read_data=None):
        self.read_data = read_data

    def read(self):
        """Read data from file."""
        return self.read_data

    def write(self, data):
        """Write data to file."""


class MockOpenWith:
    """Mock open with context manager."""

    def __init__(self, read_data=None):
        self.read_data = read_data

    def __enter__(self):
        return MockFile(read_data=self.read_data)

    def __exit__(self, *args):
        pass


def mock_open_with(read_data=None):
    """Mock open function."""
    return MockOpenWith(read_data=read_data)
