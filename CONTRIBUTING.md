# Contributing to HyprRice

Thank you for your interest in contributing to HyprRice! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Basic knowledge of Python and Qt

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hyprrice/hyprrice.git
   cd hyprrice
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Keep line length under 88 characters
- Use meaningful variable and function names

### Code Formatting
We use automated formatting tools:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run formatting before committing:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Testing
- Write tests for all new functionality
- Maintain test coverage above 85%
- Use descriptive test names
- Test both success and failure cases

### Documentation
- Update docstrings for new functions and classes
- Add type hints to all function signatures
- Update README.md for user-facing changes
- Update CHANGELOG.md for significant changes

## Plugin Development

### Creating a Plugin
1. Create a new file in the `plugins/` directory
2. Inherit from `PluginBase`
3. Implement required methods
4. Add metadata and configuration schema
5. Test your plugin thoroughly

### Plugin Guidelines
- Follow the plugin API contract
- Validate all inputs
- Handle errors gracefully
- Provide clear error messages
- Document configuration options

## Pull Request Process

### Before Submitting
1. Ensure all tests pass
2. Run code formatting tools
3. Update documentation if needed
4. Add tests for new functionality
5. Update CHANGELOG.md

### Pull Request Guidelines
- Use descriptive titles and descriptions
- Reference related issues
- Keep changes focused and atomic
- Include screenshots for GUI changes
- Test on multiple Python versions

### Review Process
- All PRs require review
- Address reviewer feedback promptly
- Keep discussions constructive
- Be open to suggestions

## Issue Reporting

### Bug Reports
When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Screenshots if applicable

### Feature Requests
For feature requests, please include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Any relevant examples

## Security

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security issues to: security@hyprrice.example.com
- Include detailed reproduction steps
- Allow time for response before public disclosure

### Security Guidelines
- Never commit secrets or credentials
- Validate all user inputs
- Use secure coding practices
- Follow principle of least privilege

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version in `__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Publish to PyPI

## Community

### Getting Help
- Check the [documentation](docs/README.md)
- Search existing issues
- Join our community discussions
- Ask questions in issues

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow community guidelines

## License

By contributing to HyprRice, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to HyprRice! 🎉
