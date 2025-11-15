# Contributing to ServiceNow MCP Server

Thank you for your interest in contributing to the ServiceNow MCP Server! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- **Clear title** describing the problem
- **Detailed description** of the issue
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, ServiceNow version)
- **Error messages or logs** if applicable

### Suggesting Features

Feature requests are welcome! Please include:

- **Clear description** of the feature
- **Use case** explaining why it's needed
- **Proposed implementation** if you have ideas
- **Examples** of how it would be used

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** by running the test suite
6. **Submit a pull request** with a clear description

## 💻 Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ServicenowMCP.git
cd ServicenowMCP
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Set Up Environment Variables

Create a `.env` file:

```env
SERVICENOW_INSTANCE=https://your-dev-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

## 📝 Coding Standards

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions **focused and small**
- Use **meaningful variable names**

### Code Example

```python
from typing import Dict, Optional

def create_incident(
    instance_url: str,
    username: str,
    password: str,
    short_description: str,
    impact: Optional[str] = None
) -> Dict[str, str]:
    """
    Create a new incident in ServiceNow.
    
    Args:
        instance_url: ServiceNow instance URL
        username: API username
        password: API password
        short_description: Brief description of the incident
        impact: Impact level (1-High, 2-Medium, 3-Low)
        
    Returns:
        Dictionary containing incident details including sys_id and number
        
    Raises:
        ValueError: If required parameters are missing
        ConnectionError: If unable to connect to ServiceNow
    """
    # Implementation here
    pass
```

### Testing

- Write **unit tests** for all new functions
- Ensure **test coverage** remains above 80%
- Use **pytest** for testing
- Mock external API calls

```python
import pytest
from unittest.mock import Mock, patch

def test_create_incident():
    """Test incident creation with valid parameters."""
    # Test implementation
    pass
```

### Documentation

- Update **README.md** for major changes
- Update **Quickstart.md** for new features
- Add **inline comments** for complex logic
- Update **CHANGELOG.md** with your changes

## 🏗️ Project Structure

```
ServicenowMCP/
├── src/
│   └── servicenow_mcp_server/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── tools/             # Tool implementations
│       │   ├── __init__.py
│       │   ├── incident.py
│       │   ├── change.py
│       │   └── ...
│       └── utils/             # Utility functions
│           ├── __init__.py
│           └── api_client.py
├── test/                      # Test suite
│   ├── test_incident.py
│   ├── test_change.py
│   └── ...
├── pyproject.toml            # Project configuration
├── README.md
├── Quickstart.md
└── CONTRIBUTING.md
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=servicenow_mcp_server

# Run specific test file
pytest test/test_incident.py

# Run with verbose output
pytest -v
```

## 📋 Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add support for knowledge base management
fix: Resolve authentication timeout issue
docs: Update installation instructions
test: Add tests for change management tools
refactor: Improve error handling in API client
```

### Commit Message Format

- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **test:** Adding or updating tests
- **refactor:** Code refactoring
- **style:** Code style changes (formatting, etc.)
- **chore:** Maintenance tasks

## 🔍 Code Review Process

1. All pull requests require **review approval**
2. Automated tests must **pass**
3. Code coverage should not **decrease**
4. Documentation must be **updated**
5. Changes should follow **coding standards**

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Reach out to the maintainer: sourojit.dhua@gmail.com

## 🙏 Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!

---

**Maintainer:** Sourojit Dhua  
**Email:** sourojit.dhua@gmail.com
