import json


def load_config(file_path='config.json'):
    """Load configuration from a JSON file.

    Args:
        file_path (str): Path to the configuration file.

    Returns:
        dict: Configuration as a dictionary.
    """
    try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        if not os.path.exists(file_path):
            log(f'Configuration file {file_path} not found. Loading default configuration.', level='warning')
            return get_default_config()
        try:
            with open(file_path) as config_file:
                return json.load(config_file)
        except json.JSONDecodeError as e:
            log(f'Error decoding JSON from {file_path}. Details: {e.msg} at line {e.lineno}, column {e.colno}', level='error')
            return get_default_config()


def get_default_config():
    '''Provide a default configuration as a fallback.'''
    return {
        'exclude_dirs': ['__pycache__', '.git', 'downloads'],
        'openai_model_name': 'gpt-4-0125-preview'
    }