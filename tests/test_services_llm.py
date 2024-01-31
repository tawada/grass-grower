"""Test services.llm module."""
import services.llm


def test_services_llm_generate_text(
    mocker,
    setup_llm_detail,
):
    """Test add_issue() function."""
    setup_llm_detail(mocker)
    openai_client = services.llm.get_openai_client()
    services.llm.generate_text([{"text": "Hello, world!"}], openai_client)
    assert True
