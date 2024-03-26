"""Module for loading configuration from a JSON file."""
import json

from utils.logging_utils import log


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
        log(f'Configuration file {file_path} not found. Loading default configuration.',
            level='warning')
        return get_default_config()
    except json.JSONDecodeError as err:
        log(f'Error decoding JSON from {file_path}. Details: {err.msg} at line {err.lineno}, column {err.colno}',
            level='error')
        return get_default_config()


def get_default_config():
    '''Provide a default configuration as a fallback.'''
    return {
        'repository_path': 'downloads',
        'exclude_dirs': ['__pycache__', '.git', 'downloads'],
        'openai_model_name': 'gpt-4-0125-preview'
    }
