"""Test module for routers_utils.py."""
from routers.routers_utils import send_messages_to_system


def test_send_messages_to_system(mocker):
    """Test send_messages_to_system function."""
    messages = [{"role": "user", "content": "テストメッセージ"}]
    system_instruction = "テスト指示"

    mock_client = mocker.MagicMock()
    mocker.patch('services.llm.get_openai_client', return_value=mock_client)
    mock_generate_text = mocker.patch('services.llm.generate_text',
                                      return_value="生成されたテキスト")

    result = send_messages_to_system(messages, system_instruction)

    expected_messages = [{
        "role": "user",
        "content": "テストメッセージ"
    }, {
        "role": "system",
        "content": "テスト指示"
    }]

    mock_generate_text.assert_called_once_with(expected_messages, mock_client)
    assert result == "生成されたテキスト"
