# Grass Grower: Enhanced Version

[![unit-test](https://github.com/tawada/grass-grower/actions/workflows/ci.yml/badge.svg)](https://github.com/tawada/grass-grower/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tawada/grass-grower/graph/badge.svg?token=SK4NPV09X0)](https://codecov.io/gh/tawada/grass-grower)
[![Maintainability](https://api.codeclimate.com/v1/badges/bfe3e9c7ac7bc6671ff1/maintainability)](https://codeclimate.com/github/tawada/grass-grower/maintainability)

Welcome to the enhanced version of Grass Grower, an AI-driven Python application formulated to automate and streamline GitHub issue management and documentation tasks. By leveraging advanced Large Language Models (LLM) capabilities, Grass Grower offers an intuitive and efficient way of handling GitHub tasks directly from the command line, providing meaningful interactions and well-structured documentation.

**Table of Contents**
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Limitations](#limitations)
- [Planned Features](#planned-features)
- [Contributing](#contributing)
- [License](#license)

## Overview

The enhanced Grass Grower tool combines AI technology with practical software project management applications. Designed for developers and project maintainers, it simplifies GitHub issue handling and README.md documentation generation through smart, AI-generated content.

## Features

- **Enhanced Automated Issue Response**: Crafts contextually aware comments for GitHub issues using AI.
- **Advanced README Generation**: Builds and updates `README.md` files that accurately represent the project's current state and technology stack.
- **Effective Codebase Analysis**: Analyzes the codebase to ensure that generated documentation and issue responses are aligned with the latest project advancements.
- **Efficient GitHub Integration**: Employs GitHub CLI for seamless interaction with GitHub repositories, facilitating issue management without the need to leave the terminal.

## Installation

Grass Grower requires Python 3.8+, OpenAI API keys, and the GitHub CLI to be installed and configured. Detailed setup and authentication steps are provided in the subsequent sections.

## Usage

Execute key functionalities of Grass Grower using these commands:

```bash
python main.py <action> [--issue-id <id>] [--repo <owner/repo>] [--branch <name>] [--code-lang <language>]
```

- `<action>`: The task to perform (e.g., `generate_code_from_issue`, `generate_readme`, `update_issue`).
- `[--issue-id <id>]`: Specifies the GitHub issue ID for actions related to issues.
- `[--repo <owner/repo>]`: Defines the GitHub repository to operate on.
- `[--branch <name>]`: Sets the repository branch for the action.
- `[--code-lang <language>]`: Indicates the primary programming language of the codebase for better context understanding by the AI.

## Configuration

Environmental variables such as OpenAI API key and default GitHub repository settings can be managed through a `config.json` file or directly within the environment settings for flexibility and security.

## Dependencies

In addition to Python 3.11, ensure the following are installed and correctly configured:

- OpenAI Python client library.
- GitHub CLI (`gh`).

Refer to the `requirements.txt` file for a detailed list of Python dependencies.

## Limitations

While Grass Grower significantly improves GitHub interaction efficiency, current limitations include:

- Single-issue interaction per command execution.
- Dependency on external APIs, implying potential costs and rate limits.

## Planned Features

Future updates aim to address existing limitations and introduce:

- Multi-issue handling for batch processing.
- Enhanced error handling and stability.
- Customizable AI-driven templates for more personalized content generation.

## Contributing

We welcome contributions from the community! Please see the repository guidelines for more information on how to contribute.

## License

Grass Grower is open-sourced under the MIT License. See the LICENSE file for legal information.
