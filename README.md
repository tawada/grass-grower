# Grass Grower

[![unit-test](https://github.com/tawada/grass-grower/actions/workflows/ci.yml/badge.svg)](https://github.com/tawada/grass-grower/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tawada/grass-grower/graph/badge.svg?token=SK4NPV09X0)](https://codecov.io/gh/tawada/grass-grower)

Welcome to Grass Grower, a cutting-edge Python application designed to streamline issue management and documentation creation for software projects on GitHub. By harnessing the capabilities of advanced Large Language Models (LLMs), our tool can autonomously generate meaningful responses to issues and produce comprehensive and accurate `README.md` documentation.

**Table of Contents**
- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Overview

Grass Grower is engineered to bridge the gap between project maintenance and AI technology. The tool efficiently facilitates developers to manage GitHub issues and autogenerate documentation by providing relevant, smart, and concise LLM-generated content.

## Features

Grass Grower is packed with an array of features to elevate your software project management:

- **Automated Issue Response**: Utilizes AI to craft well-thought-out and context-aware comments as responses to GitHub issues.
- **Dynamic Documentation Generation**: Analyzes the codebase and employed technologies to compose an updated and informative `README.md`.
- **Codebase Analysis**: Scans and interprets the entire codebase, ensuring the documentation aligns with the latest developments.
- **Direct GitHub Integration**: Directly communicates with GitHub via CLI to fetch issues and submit replies without leaving the command line.

## How It Works

Grass Grower is composed of multiple modules, each designed to perform specialized operations:

- `main.py`: Serves as the command center, accepting arguments and deploying corresponding actions like generating readmes or issue updates.
- `routers`: Contains the core logic for readme generation and issue management.
- `services`: Interfaces with GitHub (`github`) for issue retrieval and comments while leveraging LLMs (`llm`) for content creation.
- `schemas`: Defines essential data structures like the `Issue` class for systematic data handling.
- `system_instruction`: Interprets user-generated system commands to guide the AI model.

## Getting Started

To harness the power of Grass Grower, set up your environment:

1. Install and configure the GitHub CLI (`gh`).
2. Ensure OpenAI API keys are properly set up for LLM interactions.

## Usage

Activate Grass Grower with these simple commands:

```bash
python main.py generate_code_from_issue [issue_id] # Generate code for a specific issue
python main.py generate_readme                    # Generate the README.md file
python main.py update_issue                       # Post a comment on an existing issue
```

Replace `[issue_id]` with the actual ID of the GitHub issue you're addressing.

## Dependencies

- Python 3.8 or later
- OpenAI's Python client
- GitHub CLI (`gh`)

## Limitations

Grass Grower comes with certain constraints:

- Interaction is currently limited to the first retrieved GitHub issue.
- Reliant on OpenAI's API, potentially incurring additional costs and rate limits.

## Future Enhancements

Projected enhancements include:

- Multi-issue interaction capability.
- Refined error handling for improved stability.
- More sophisticated AI-driven content creation tailored to user input.

## Contributing

Contributors are welcome to join the development of Grass Grower. Feel free to fork the repository, make improvements, and open pull requests.

## License

Grass Grower is released under the MIT License. See the LICENSE file for more details.

*Authored with AI enhancement.*
