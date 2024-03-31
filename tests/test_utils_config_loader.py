"""Test utils.config_loader module."""
from pytest_mock import MockFixture

import utils.config_loader


def test_utils_config_loader_from_file(mocker: MockFixture, ):
    """Test utils.config_loader.load_config."""
    mocker.patch("builtins.open",
                 mocker.mock_open(read_data='{"json_test": "test"}'))
    config = utils.config_loader.load_config()
    assert config["json_test"] == "test"


def test_utils_config_loader_with_file_not_found():
    """Test utils.config_loader.load_config."""
    config = utils.config_loader.load_config()
    assert config == utils.config_loader.get_default_config()


def test_utils_config_loader_with_json_decoded_error(mocker: MockFixture, ):
    """Test utils.config_loader.load_config."""
    mocker.patch("builtins.open", mocker.mock_open(read_data="not a json"))
    config = utils.config_loader.load_config()
    assert config == utils.config_loader.get_default_config()
