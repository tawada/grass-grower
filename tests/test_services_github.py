"""Test services.github module."""
import services.github


def test_services_github_setup_repository_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=True,
    )
    services.github.setup_repository("test/test")
    assert True


def test_services_github_setup_repository_not_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=False,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=True,
    )
    services.github.setup_repository("test/test")
    assert True
