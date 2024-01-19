import routers


def test_add_issue(
    mocker,
    setup,
):
    """Test add_issue() function."""
    setup(mocker)
    routers.add_issue("test_owner/test_repo")
    assert True


def test_update_issue(
    mocker,
    setup,
):
    """Test update_issue() function."""
    setup(mocker)
    routers.update_issue("test_owner/test_repo", 1)
    assert True


def test_generate_code_from_issue(mocker, setup):
    """Test generate_code_from_issue() function."""
    setup(mocker)
    routers.generate_code_from_issue("test_owner/test_repo", 1)
    assert True


def test_summarize_issue(mocker, setup):
    """Test summarize_issue() function."""
    setup(mocker)
    routers.summarize_issue("test_owner/test_repo", 1)
    assert True


def generate_readme(mocker, setup):
    """Test generate_readme() function."""
    setup(mocker)
    routers.generate_readme("test_owner/test_repo")
    assert True
