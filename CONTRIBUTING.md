# Contributing to AI Personal Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/AI-PERSONAL-AGENT.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov pytest-mock

# Run tests
pytest

# Run tests with coverage
pytest --cov=ai_assistant --cov-report=html
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage (>80%)
- Use mocking for external API calls

## Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Include usage examples for new features
- Update .env.example if adding new configuration options

## Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG if applicable
5. Get approval from maintainers
6. Squash commits if requested

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Relevant logs

## Feature Requests

For feature requests, please:

- Check if the feature already exists
- Describe the use case
- Explain why it would be useful
- Suggest an implementation approach

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions professional

## Questions?

Feel free to open an issue for any questions or concerns.

Thank you for contributing!
