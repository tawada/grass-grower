"""Test routers.py module."""
from datetime import datetime, timedelta

import routers


def test_add_issue(
    mocker,
    setup,
):
    """Test add_issue() function."""
    setup(mocker)
    routers.add_issue("test_owner/test_repo", "python")


def test_update_issue(
    mocker,
    setup,
):
    """Test update_issue() function."""
    setup(mocker)
    routers.update_issue(1, "test_owner/test_repo", "main", "python")


def test_generate_code_from_issue(mocker, setup):
    """Test generate_code_from_issue() function."""
    setup(mocker)
    routers.generate_code_from_issue(1, "test_owner/test_repo", "main",
                                     "python")


def test_summarize_issue(mocker, setup):
    """Test summarize_issue() function."""
    setup(mocker)
    routers.summarize_issue(1, "test_owner/test_repo", "main")


def test_generate_readme(mocker, setup):
    """Test generate_readme() function."""
    setup(mocker)
    routers.generate_readme("test_owner/test_repo", "main", "python")


def test_generate_readme_failed(mocker, setup):
    """Test generate_readme() function."""
    setup(mocker)

    class DummyFileController:
        """Dummy file controller class."""

        def __enter__(self):
            return type("FileController", (object, ), {
                "read": lambda: "test",
                "write": lambda *args: True
            })

        def __exit__(self, *args):
            pass

    mocker.patch("routers.open", return_value=DummyFileController())
    routers.generate_readme("test_owner/test_repo", "main", "python")


def test_grow_grass_now(mocker, setup):
    """Test grow_grass() function."""
    setup(mocker)
    mocker.patch("services.github.get_datetime_of_last_commit",
                 return_value=datetime.now())
    routers.grow_grass("test_owner/test_repo", "main", "python")


def test_grow_grass_yesterday(mocker, setup):
    """Test grow_grass() function."""
    setup(mocker)
    mocker.patch("services.github.get_datetime_of_last_commit",
                 return_value=datetime.now() - timedelta(days=1))
    routers.grow_grass("test_owner/test_repo", "main", "python")
