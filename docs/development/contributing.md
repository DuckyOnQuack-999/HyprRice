# Contributing to HyprRice

Thank you for your interest in contributing to HyprRice! This guide will help you get started.

## Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/hyprrice.git
   cd hyprrice
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   ```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature
```

### 2. Make Changes
- Follow coding style (PEP 8)
- Add tests for new features
- Update documentation

### 3. Test Changes
```bash
# Run tests
pytest tests/

# Run linter
flake8 src/ tests/

# Check types
mypy src/
```

### 4. Submit Changes
1. Commit your changes
2. Push to your fork
3. Create a pull request

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small

### Example
```python
from typing import Dict, Any

def process_config(config: Dict[str, Any]) -> bool:
    """
    Process and validate configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(config, dict):
        return False
    
    # Process config
    return True
```

## Testing

### Writing Tests
```python
def test_process_config():
    """Test configuration processing."""
    # Setup
    config = {"key": "value"}
    
    # Execute
    result = process_config(config)
    
    # Assert
    assert result is True
```

### Running Tests
```bash
# All tests
pytest

# Specific test
pytest tests/test_config.py

# With coverage
pytest --cov=src/
```

## Documentation

### Code Documentation
- Use docstrings (Google style)
- Include type hints
- Document exceptions
- Add usage examples

### User Documentation
- Update relevant .md files
- Add new features to user guide
- Include screenshots if needed
- Update troubleshooting

## Pull Request Process

1. **Before Submitting**
   - Tests pass
   - Documentation updated
   - Code formatted
   - Changes described

2. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation
   - [ ] Other
   
   ## Testing
   How were changes tested?
   
   ## Screenshots
   If applicable
   ```

3. **Review Process**
   - Address feedback
   - Keep PR focused
   - Update as needed

## Release Process

1. **Version Bump**
   - Update version in setup.py
   - Update CHANGELOG.md
   - Tag release

2. **Documentation**
   - Update version references
   - Check all examples
   - Verify links

3. **Testing**
   - Run full test suite
   - Test installation
   - Verify dependencies

## Community

- Be respectful
- Follow code of conduct
- Help others
- Share knowledge

## Resources

- [Development Setup](setup.md)
- [Testing Guide](testing.md)
- [User Guide](../user_guide.md)
- [API Reference](../reference/plugin_api.md) 