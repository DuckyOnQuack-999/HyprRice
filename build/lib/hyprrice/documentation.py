"""
Documentation Generation System for HyprRice

Automatically generates comprehensive documentation from code,
configuration schemas, and plugin metadata.
"""

import os
import json
import yaml
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

from .plugins import PluginBase, PluginMetadata
from .config import Config
from .security import input_validator


@dataclass
class DocumentationSection:
    """Represents a section of documentation."""
    title: str
    content: str
    subsections: List['DocumentationSection'] = None
    code_examples: List[str] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []
        if self.code_examples is None:
            self.code_examples = []


class DocumentationGenerator:
    """Generates comprehensive documentation for HyprRice."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Documentation sections
        self.sections = {}
    
    def generate_all_documentation(self):
        """Generate all documentation."""
        self.logger.info("Generating comprehensive documentation...")
        
        # Generate different documentation types
        self.generate_api_documentation()
        self.generate_configuration_documentation()
        self.generate_plugin_documentation()
        self.generate_security_documentation()
        self.generate_troubleshooting_documentation()
        self.generate_development_documentation()
        
        # Generate index
        self.generate_index()
        
        self.logger.info(f"Documentation generated in {self.output_dir}")
    
    def generate_api_documentation(self):
        """Generate API documentation from code."""
        api_doc = DocumentationSection(
            title="API Documentation",
            content="Complete API reference for HyprRice components."
        )
        
        # Document main classes
        from . import config, plugins, utils, security
        
        modules = {
            'Configuration': config,
            'Plugin System': plugins,
            'Utilities': utils,
            'Security': security
        }
        
        for module_name, module in modules.items():
            module_section = self._document_module(module, module_name)
            api_doc.subsections.append(module_section)
        
        self._write_documentation("api.md", api_doc)
    
    def generate_configuration_documentation(self):
        """Generate configuration documentation."""
        config_doc = DocumentationSection(
            title="Configuration Guide",
            content="Complete guide to configuring HyprRice."
        )
        
        # Document configuration structure
        config_schema = self._extract_config_schema()
        
        config_doc.subsections.append(DocumentationSection(
            title="Configuration Structure",
            content=self._generate_config_structure_docs(config_schema)
        ))
        
        config_doc.subsections.append(DocumentationSection(
            title="Configuration Examples",
            content="Common configuration examples and use cases.",
            code_examples=self._generate_config_examples()
        ))
        
        config_doc.subsections.append(DocumentationSection(
            title="Migration Guide",
            content=self._generate_migration_docs()
        ))
        
        self._write_documentation("configuration.md", config_doc)
    
    def generate_plugin_documentation(self):
        """Generate plugin system documentation."""
        plugin_doc = DocumentationSection(
            title="Plugin Development Guide",
            content="Complete guide to developing plugins for HyprRice."
        )
        
        # Plugin development guide
        plugin_doc.subsections.append(DocumentationSection(
            title="Getting Started",
            content=self._generate_plugin_getting_started()
        ))
        
        plugin_doc.subsections.append(DocumentationSection(
            title="Plugin API Reference",
            content=self._generate_plugin_api_docs()
        ))
        
        plugin_doc.subsections.append(DocumentationSection(
            title="Security Considerations",
            content=self._generate_plugin_security_docs()
        ))
        
        plugin_doc.subsections.append(DocumentationSection(
            title="Example Plugins",
            content="Complete example plugins with explanations.",
            code_examples=self._generate_plugin_examples()
        ))
        
        self._write_documentation("plugins.md", plugin_doc)
    
    def generate_security_documentation(self):
        """Generate security documentation."""
        security_doc = DocumentationSection(
            title="Security Guide",
            content="Security features and best practices for HyprRice."
        )
        
        security_doc.subsections.append(DocumentationSection(
            title="Security Features",
            content=self._generate_security_features_docs()
        ))
        
        security_doc.subsections.append(DocumentationSection(
            title="Plugin Sandboxing",
            content=self._generate_sandboxing_docs()
        ))
        
        security_doc.subsections.append(DocumentationSection(
            title="Input Validation",
            content=self._generate_validation_docs()
        ))
        
        security_doc.subsections.append(DocumentationSection(
            title="Best Practices",
            content=self._generate_security_best_practices()
        ))
        
        self._write_documentation("security.md", security_doc)
    
    def generate_troubleshooting_documentation(self):
        """Generate troubleshooting documentation."""
        troubleshooting_doc = DocumentationSection(
            title="Troubleshooting Guide",
            content="Common issues and solutions for HyprRice."
        )
        
        # Common issues
        issues = [
            {
                "title": "Plugin Loading Issues",
                "content": self._generate_plugin_troubleshooting()
            },
            {
                "title": "Configuration Errors",
                "content": self._generate_config_troubleshooting()
            },
            {
                "title": "Performance Issues",
                "content": self._generate_performance_troubleshooting()
            },
            {
                "title": "Security Warnings",
                "content": self._generate_security_troubleshooting()
            }
        ]
        
        for issue in issues:
            troubleshooting_doc.subsections.append(DocumentationSection(
                title=issue["title"],
                content=issue["content"]
            ))
        
        self._write_documentation("troubleshooting.md", troubleshooting_doc)
    
    def generate_development_documentation(self):
        """Generate development documentation."""
        dev_doc = DocumentationSection(
            title="Development Guide",
            content="Guide for contributing to HyprRice development."
        )
        
        dev_doc.subsections.append(DocumentationSection(
            title="Development Setup",
            content=self._generate_dev_setup_docs()
        ))
        
        dev_doc.subsections.append(DocumentationSection(
            title="Testing",
            content=self._generate_testing_docs()
        ))
        
        dev_doc.subsections.append(DocumentationSection(
            title="Code Style",
            content=self._generate_code_style_docs()
        ))
        
        dev_doc.subsections.append(DocumentationSection(
            title="Contributing",
            content=self._generate_contributing_docs()
        ))
        
        self._write_documentation("development.md", dev_doc)
    
    def generate_index(self):
        """Generate documentation index."""
        index_content = f"""# HyprRice Documentation

Welcome to the comprehensive documentation for HyprRice - a modern GUI tool for customizing Hyprland and its ecosystem.

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Quick Start

1. [Installation Guide](installation.md)
2. [Configuration Guide](configuration.md)
3. [Plugin System](plugins.md)

## Documentation Sections

### User Guides
- **[Configuration Guide](configuration.md)** - Complete configuration reference
- **[Plugin Guide](plugins.md)** - Using and developing plugins
- **[Security Guide](security.md)** - Security features and best practices
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### Developer Documentation
- **[API Documentation](api.md)** - Complete API reference
- **[Development Guide](development.md)** - Contributing to HyprRice
- **[Testing Guide](testing.md)** - Running and writing tests

## Features

### Core Features
- **Modern GUI** - Intuitive interface for Hyprland configuration
- **Theme Management** - Create, apply, and share themes
- **Plugin System** - Extensible architecture with sandboxing
- **Configuration Backup** - Automatic backup and restore
- **Live Preview** - Real-time configuration preview

### Security Features
- **Input Validation** - Comprehensive input sanitization
- **Plugin Sandboxing** - Secure plugin execution environment
- **Path Restrictions** - Prevent path traversal attacks
- **Command Sanitization** - Safe hyprctl command execution

### Performance Features
- **Async Operations** - Non-blocking UI operations
- **Caching System** - Intelligent caching with TTL
- **Memory Management** - Leak detection and prevention
- **Performance Monitoring** - Built-in performance tracking

## System Requirements

- **Operating System**: Linux with Wayland support
- **Window Manager**: Hyprland
- **Python**: 3.8 or higher
- **Dependencies**: PyQt5/PySide6, PyYAML, psutil

## Support

- **Issues**: Report issues on the project repository
- **Documentation**: This documentation covers all aspects of HyprRice
- **Community**: Join our community discussions

---

*HyprRice - Making Hyprland configuration beautiful and accessible.*
"""
        
        with open(self.output_dir / "index.md", 'w') as f:
            f.write(index_content)
    
    def _document_module(self, module, module_name: str) -> DocumentationSection:
        """Document a Python module."""
        section = DocumentationSection(
            title=module_name,
            content=f"API documentation for {module_name} module."
        )
        
        # Get module docstring
        if hasattr(module, '__doc__') and module.__doc__:
            section.content = module.__doc__.strip()
        
        # Document classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                class_section = self._document_class(obj, name)
                section.subsections.append(class_section)
        
        # Document functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module.__name__:
                func_section = self._document_function(obj, name)
                section.subsections.append(func_section)
        
        return section
    
    def _document_class(self, cls: Type, class_name: str) -> DocumentationSection:
        """Document a class."""
        section = DocumentationSection(
            title=f"Class: {class_name}",
            content=cls.__doc__ or f"Class {class_name}"
        )
        
        # Document methods
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if not name.startswith('_'):
                method_section = self._document_function(method, name)
                section.subsections.append(method_section)
        
        return section
    
    def _document_function(self, func, func_name: str) -> DocumentationSection:
        """Document a function."""
        signature = inspect.signature(func)
        docstring = func.__doc__ or f"Function {func_name}"
        
        content = f"""
### {func_name}

**Signature**: `{func_name}{signature}`

{docstring}
"""
        
        return DocumentationSection(
            title=f"Function: {func_name}",
            content=content.strip()
        )
    
    def _extract_config_schema(self) -> Dict[str, Any]:
        """Extract configuration schema from Config class."""
        config = Config()
        schema = {}
        
        for field_name in ['general', 'paths', 'gui', 'hyprland', 'waybar', 'rofi', 'notifications', 'clipboard', 'lockscreen']:
            if hasattr(config, field_name):
                field_obj = getattr(config, field_name)
                schema[field_name] = self._extract_dataclass_schema(field_obj)
        
        return schema
    
    def _extract_dataclass_schema(self, obj) -> Dict[str, Any]:
        """Extract schema from a dataclass object."""
        if not hasattr(obj, '__dataclass_fields__'):
            return {}
        
        schema = {}
        for field_name, field in obj.__dataclass_fields__.items():
            schema[field_name] = {
                'type': str(field.type),
                'default': getattr(obj, field_name),
                'description': f"Configuration for {field_name}"
            }
        
        return schema
    
    def _generate_config_structure_docs(self, schema: Dict[str, Any]) -> str:
        """Generate configuration structure documentation."""
        content = "## Configuration Structure\n\n"
        content += "HyprRice uses a hierarchical configuration structure:\n\n"
        
        for section_name, section_schema in schema.items():
            content += f"### {section_name.title()} Section\n\n"
            
            for field_name, field_info in section_schema.items():
                content += f"- **{field_name}** (`{field_info['type']}`): {field_info['description']}\n"
                content += f"  - Default: `{field_info['default']}`\n\n"
        
        return content
    
    def _generate_config_examples(self) -> List[str]:
        """Generate configuration examples."""
        examples = []
        
        # Basic configuration example
        basic_example = """
# Basic HyprRice Configuration
general:
  theme: "dark"
  auto_backup: true
  backup_retention: 10

gui:
  window_width: 1200
  window_height: 800
  auto_save: true
  auto_save_interval: 30

hyprland:
  border_color: "#89b4fa"
  gaps_in: 5
  gaps_out: 10
  blur_enabled: true

plugins:
  enabled: true
  auto_load:
    - terminal_theming
    - notification_theming
  security_level: "medium"
"""
        examples.append(basic_example.strip())
        
        # Advanced configuration example
        advanced_example = """
# Advanced HyprRice Configuration
general:
  theme: "catppuccin"
  auto_backup: true
  backup_retention: 20
  encrypt_backups: true

security:
  input_validation: true
  path_restrictions: true
  command_sanitization: true
  file_size_limits: true

performance:
  monitoring_enabled: true
  cache_size: 2000
  cache_ttl: 600

plugins:
  enabled: true
  sandbox_enabled: true
  security_level: "strict"
  auto_load:
    - terminal_theming
    - notification_theming
    - wallpaper_manager
"""
        examples.append(advanced_example.strip())
        
        return examples
    
    def _generate_migration_docs(self) -> str:
        """Generate migration documentation."""
        return """
## Configuration Migration

HyprRice automatically handles configuration migration between versions.

### Automatic Migration

When you start HyprRice with an older configuration file, it will:

1. **Create a backup** of your current configuration
2. **Migrate the configuration** to the latest format
3. **Validate the result** to ensure correctness
4. **Apply the changes** and continue startup

### Manual Migration

You can also migrate configurations manually:

```bash
# Check if migration is needed
python -m hyprrice.migration --check ~/.config/hyprrice/config.yaml

# Perform migration
python -m hyprrice.migration ~/.config/hyprrice/config.yaml

# Migrate without backup (not recommended)
python -m hyprrice.migration --no-backup ~/.config/hyprrice/config.yaml
```

### Migration Versions

- **0.1.0 → 0.2.0**: Added plugin system configuration
- **0.2.0 → 0.3.0**: Restructured theme configuration
- **0.3.0 → 1.0.0**: Added security and performance settings
"""
    
    def _generate_plugin_getting_started(self) -> str:
        """Generate plugin getting started guide."""
        return """
## Getting Started with Plugin Development

### Basic Plugin Structure

Every HyprRice plugin must inherit from `PluginBase` and implement the `metadata` property:

```python
from src.hyprrice.plugins import PluginBase, PluginMetadata

class MyPlugin(PluginBase):
    @property
    def metadata(self):
        return PluginMetadata(
            name="My Plugin",
            version="1.0.0",
            description="A sample plugin",
            author="Your Name",
            dependencies=[],
            config_schema={
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable this plugin"
                }
            }
        )
    
    def register(self, app):
        super().register(app)
        self.logger.info("Plugin registered successfully")
    
    def after_theme_change(self, context):
        # React to theme changes
        colors = context.get('colors', {})
        self.logger.info(f"Theme changed: {colors}")

# Required: plugin entry point
plugin_class = MyPlugin
```

### Plugin Lifecycle

1. **Discovery**: Plugin files are scanned from the plugins directory
2. **Loading**: Plugin class is instantiated and validated
3. **Registration**: Plugin is registered with the main application
4. **Event Handling**: Plugin receives events and can react to them
5. **Unloading**: Plugin is cleanly shut down when disabled

### Event System

Plugins can handle various events:

- `before_apply`: Before applying configuration to Hyprland
- `after_apply`: After applying configuration to Hyprland
- `before_theme_change`: Before changing themes
- `after_theme_change`: After changing themes
- `on_startup`: When plugin is loaded
- `on_shutdown`: When plugin is unloaded
"""
    
    def _generate_plugin_api_docs(self) -> str:
        """Generate plugin API documentation."""
        return """
## Plugin API Reference

### PluginBase Class

Base class for all HyprRice plugins.

#### Required Methods

- `metadata` (property): Returns `PluginMetadata` object with plugin information

#### Optional Methods

- `register(app)`: Called when plugin is registered with the application
- `configure(config)`: Called when plugin configuration changes
- `validate_dependencies()`: Validate plugin dependencies

#### Event Handlers

All event handlers are optional and receive a context dictionary:

- `before_apply(context)`: Called before applying configuration
- `after_apply(context)`: Called after applying configuration
- `before_theme_change(context)`: Called before theme changes
- `after_theme_change(context)`: Called after theme changes
- `on_startup(context)`: Called when plugin starts
- `on_shutdown(context)`: Called when plugin shuts down

### PluginMetadata Class

Contains plugin metadata information:

- `name`: Human-readable plugin name
- `version`: Plugin version (semantic versioning)
- `description`: Brief description of plugin functionality
- `author`: Plugin author name
- `dependencies`: List of required Python modules
- `config_schema`: JSON schema for plugin configuration
"""
    
    def _generate_plugin_security_docs(self) -> str:
        """Generate plugin security documentation."""
        return """
## Plugin Security

### Sandboxing

HyprRice runs plugins in a secure sandbox environment that:

- **Restricts file system access** to allowed directories only
- **Limits resource usage** (memory, CPU, file descriptors)
- **Blocks dangerous operations** (exec, eval, subprocess)
- **Validates imports** to prevent loading dangerous modules

### Security Levels

- **Strict**: Maximum security, minimal permissions
- **Medium**: Balanced security and functionality (default)
- **Relaxed**: Fewer restrictions for trusted plugins

### Best Practices

1. **Minimal Permissions**: Request only the permissions you need
2. **Input Validation**: Always validate user inputs
3. **Error Handling**: Handle errors gracefully
4. **Resource Cleanup**: Clean up resources properly
5. **Dependency Management**: Minimize external dependencies
"""
    
    def _generate_plugin_examples(self) -> List[str]:
        """Generate plugin examples."""
        return [
            """
# Terminal Theming Plugin Example
from src.hyprrice.plugins import PluginBase, PluginMetadata
from pathlib import Path

class TerminalThemingPlugin(PluginBase):
    @property
    def metadata(self):
        return PluginMetadata(
            name="Terminal Theming",
            version="1.0.0",
            description="Apply themes to terminal emulators",
            author="HyprRice Team",
            config_schema={
                "terminals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["kitty", "alacritty"]
                }
            }
        )
    
    def after_theme_change(self, context):
        colors = context.get('colors', {})
        terminals = self.config.get('terminals', [])
        
        for terminal in terminals:
            self.apply_terminal_theme(terminal, colors)
    
    def apply_terminal_theme(self, terminal, colors):
        if terminal == "kitty":
            self.apply_kitty_theme(colors)
        elif terminal == "alacritty":
            self.apply_alacritty_theme(colors)

plugin_class = TerminalThemingPlugin
""".strip()
        ]
    
    def _generate_security_features_docs(self) -> str:
        """Generate security features documentation."""
        return """
## Security Features

### Input Validation

All user inputs are validated and sanitized:

- **Path Validation**: Prevents path traversal attacks
- **Command Sanitization**: Prevents command injection
- **File Size Limits**: Prevents resource exhaustion
- **Content Validation**: Validates configuration data

### Plugin Sandboxing

Plugins run in a restricted environment:

- **Resource Limits**: Memory, CPU, and file descriptor limits
- **File System Restrictions**: Access only to allowed directories
- **Import Restrictions**: Only safe modules can be imported
- **Execution Restrictions**: Dangerous functions are blocked

### Configuration Security

- **Secure File Handling**: Safe YAML/JSON parsing
- **Backup Encryption**: Optional encryption for sensitive data
- **Permission Checking**: Validates file permissions
- **Atomic Operations**: Prevents partial writes
"""
    
    def _generate_sandboxing_docs(self) -> str:
        """Generate sandboxing documentation."""
        return """
## Plugin Sandboxing

### How It Works

The sandbox system creates a restricted execution environment:

1. **Resource Limits**: Sets system resource limits (memory, CPU, file descriptors)
2. **Import Filtering**: Intercepts and filters module imports
3. **File System Guards**: Restricts file system access to allowed paths
4. **Function Restrictions**: Replaces dangerous built-in functions

### Configuration

Sandboxing can be configured per plugin:

```yaml
plugins:
  sandbox_enabled: true
  security_level: "medium"  # strict, medium, relaxed
  
  # Per-plugin configuration
  plugin_config:
    my_plugin:
      sandbox_level: "strict"
      allowed_paths:
        - "~/.config/my_app"
      resource_limits:
        memory_mb: 50
        cpu_seconds: 10
```

### Debugging Sandbox Issues

If plugins fail due to sandbox restrictions:

1. Check the logs for specific error messages
2. Temporarily disable sandboxing for testing
3. Adjust security level or resource limits
4. Add required paths to allowed_paths list
"""
    
    def _generate_validation_docs(self) -> str:
        """Generate validation documentation."""
        return """
## Input Validation

### Validation Types

- **Path Validation**: Ensures paths are safe and within allowed directories
- **Color Validation**: Validates color formats (hex, rgb, rgba)
- **Theme Validation**: Validates theme file structure and content
- **Configuration Validation**: Validates configuration schema

### Custom Validation

You can add custom validation rules:

```python
from src.hyprrice.security import input_validator

# Validate custom format
def validate_my_format(value):
    if not my_custom_check(value):
        raise ValidationError("Invalid format")
    return value

# Use in your code
validated_value = validate_my_format(user_input)
```
"""
    
    def _generate_security_best_practices(self) -> str:
        """Generate security best practices."""
        return """
## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version
2. **Review Plugins**: Only install plugins from trusted sources
3. **Enable Sandboxing**: Keep plugin sandboxing enabled
4. **Regular Backups**: Maintain regular configuration backups
5. **Monitor Logs**: Check logs for security warnings

### For Plugin Developers

1. **Validate Inputs**: Always validate user inputs
2. **Minimal Permissions**: Request only necessary permissions
3. **Secure Coding**: Follow secure coding practices
4. **Error Handling**: Handle errors gracefully
5. **Documentation**: Document security considerations

### For System Administrators

1. **File Permissions**: Set appropriate file permissions
2. **Network Security**: Consider network access restrictions
3. **Resource Limits**: Set appropriate system resource limits
4. **Monitoring**: Monitor for suspicious activity
5. **Updates**: Keep system dependencies updated
"""
    
    def _write_documentation(self, filename: str, section: DocumentationSection):
        """Write documentation section to file."""
        content = self._render_section(section)
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.debug(f"Generated documentation: {filepath}")
    
    def _render_section(self, section: DocumentationSection, level: int = 1) -> str:
        """Render a documentation section to markdown."""
        content = ""
        
        # Section title
        content += "#" * level + " " + section.title + "\n\n"
        
        # Section content
        if section.content:
            content += section.content + "\n\n"
        
        # Code examples
        if section.code_examples:
            content += "## Examples\n\n"
            for i, example in enumerate(section.code_examples, 1):
                content += f"### Example {i}\n\n"
                content += "```yaml\n" + example + "\n```\n\n"
        
        # Subsections
        for subsection in section.subsections:
            content += self._render_section(subsection, level + 1)
        
        return content
    
    def _generate_dev_setup_docs(self) -> str:
        """Generate development setup documentation."""
        return """
## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hyprrice/hyprrice.git
   cd hyprrice
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

5. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

### Development Tools

- **Linting**: `flake8`, `pylint`
- **Formatting**: `black`, `isort`
- **Type Checking**: `mypy`
- **Testing**: `pytest`, `coverage`
"""
    
    def _generate_testing_docs(self) -> str:
        """Generate testing documentation."""
        return """
## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/hyprrice

# Run specific test file
python -m pytest tests/test_config.py

# Run with verbose output
python -m pytest tests/ -v
```

### Test Types

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Security Tests**: Test security features
- **Performance Tests**: Test performance characteristics

### Writing Tests

```python
import unittest
from src.hyprrice.testing import SecurityTestCase, PerformanceTestCase

class MySecurityTest(SecurityTestCase):
    def test_input_validation(self):
        # Test security features
        pass

class MyPerformanceTest(PerformanceTestCase):
    def test_operation_performance(self):
        # Test performance
        pass
```
"""
    
    def _generate_code_style_docs(self) -> str:
        """Generate code style documentation."""
        return """
## Code Style

### Python Style Guide

Follow PEP 8 with these additions:

- **Line Length**: 100 characters maximum
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for all public functions

### Formatting

Use `black` for code formatting:

```bash
black src/ tests/
```

Use `isort` for import sorting:

```bash
isort src/ tests/
```

### Linting

Use `flake8` for linting:

```bash
flake8 src/ tests/
```

### Documentation

- Document all public classes and functions
- Include examples in docstrings
- Keep documentation up to date with code changes
"""
    
    def _generate_contributing_docs(self) -> str:
        """Generate contributing documentation."""
        return """
## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Pull Request Guidelines

- **Clear Description**: Describe what your PR does and why
- **Tests**: Include tests for new features
- **Documentation**: Update documentation as needed
- **Code Style**: Follow the project's code style
- **Small Changes**: Keep PRs focused and reasonably sized

### Issue Reporting

When reporting issues:

- **Clear Title**: Summarize the issue clearly
- **Reproduction Steps**: Provide steps to reproduce
- **Environment**: Include OS, Python version, etc.
- **Logs**: Include relevant log output
- **Expected Behavior**: Describe what should happen

### Feature Requests

For feature requests:

- **Use Case**: Explain why the feature is needed
- **Alternatives**: Consider alternative solutions
- **Implementation**: Suggest how it might work
- **Breaking Changes**: Note any breaking changes
"""
    
    def _generate_plugin_troubleshooting(self) -> str:
        """Generate plugin troubleshooting documentation."""
        return """
### Plugin Loading Issues

**Problem**: Plugin fails to load

**Solutions**:
- Check plugin file syntax
- Verify plugin class is properly defined
- Check dependencies are installed
- Review sandbox restrictions
- Check file permissions

**Problem**: Plugin crashes on startup

**Solutions**:
- Check plugin initialization code
- Verify configuration is valid
- Review resource limits
- Check for missing dependencies
"""
    
    def _generate_config_troubleshooting(self) -> str:
        """Generate configuration troubleshooting documentation."""
        return """
### Configuration Errors

**Problem**: Configuration file fails to load

**Solutions**:
- Check YAML syntax
- Verify file permissions
- Check for invalid values
- Try with default configuration

**Problem**: Settings not applied

**Solutions**:
- Restart HyprRice
- Check Hyprland is running
- Verify configuration paths
- Check for validation errors
"""
    
    def _generate_performance_troubleshooting(self) -> str:
        """Generate performance troubleshooting documentation."""
        return """
### Performance Issues

**Problem**: High memory usage

**Solutions**:
- Check for memory leaks
- Reduce cache size
- Disable unnecessary plugins
- Monitor resource usage

**Problem**: Slow startup

**Solutions**:
- Reduce plugin count
- Check disk I/O
- Clear old cache files
- Optimize configuration
"""
    
    def _generate_security_troubleshooting(self) -> str:
        """Generate security troubleshooting documentation."""
        return """
### Security Warnings

**Problem**: Path traversal warnings

**Solutions**:
- Check file paths in configuration
- Verify plugin file access
- Review allowed paths
- Update path restrictions

**Problem**: Sandbox violations

**Solutions**:
- Adjust security level
- Add required permissions
- Update plugin code
- Check resource limits
"""


def generate_documentation():
    """Convenience function to generate all documentation."""
    generator = DocumentationGenerator()
    generator.generate_all_documentation()


if __name__ == "__main__":
    generate_documentation()
