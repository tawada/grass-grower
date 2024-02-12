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
        print(f'Configuration file {file_path} not found.')
        return {}
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON from {file_path}: {e}')
        return {}