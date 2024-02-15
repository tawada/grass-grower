"""Test services.llm module."""
import services.llm


def test_services_llm_generate_text(
    mocker,
    setup_llm_detail,
):
    """Test llm.generate_text() function."""
    setup_llm_detail(mocker)
    openai_client = services.llm.get_openai_client()
    services.llm.generate_text([{"text": "Hello, world!"}], openai_client)
    assert True


def test_services_llm_generate_json(
    mocker,
    setup_llm_detail,
):
    """Test llm.generate_json() function."""
    setup_llm_detail(mocker)
    openai_client = services.llm.get_openai_client()
    services.llm.generate_json([{"text": "Hello, world!"}], openai_client)
    assert True
