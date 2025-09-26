# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- Initial public release of HyprRice
- Comprehensive GUI for Hyprland theme management
- CLI interface with commands: `gui`, `check`, `migrate`, `plugins`, `doctor`
- Plugin system with sandboxing and security controls
- Theme import/export functionality with validation
- Backup and restore system for configurations
- Real-time preview with Hyprland integration
- Performance monitoring and profiling
- Security validation and input sanitization
- Configuration migration system
- Comprehensive documentation generation
- CI/CD pipeline with automated testing and PyPI publishing

### Features
- **Theme Management**: Create, edit, import, and export Hyprland themes
- **Plugin System**: Extensible architecture with terminal and notification theming plugins
- **Security**: Input validation, path sanitization, and plugin sandboxing
- **Performance**: Caching, async operations, and background workers
- **User Experience**: Keyboard shortcuts, error handling, and user-friendly dialogs
- **Integration**: Direct Hyprland integration via `hyprctl` commands
- **Documentation**: Auto-generated API docs and user guides

### Technical Details
- Python 3.10+ support
- PyQt5 GUI framework
- YAML configuration format
- JSON schema validation
- Plugin metadata and configuration system
- Comprehensive test suite
- Type hints throughout codebase

### Security
- Input validation and sanitization
- Path traversal prevention
- Command injection protection
- Plugin sandboxing with resource limits
- Secure file I/O operations

### Performance
- Caching for `hyprctl` commands
- Asynchronous operations
- Background workers for heavy tasks
- Memory usage monitoring
- Profiling decorators

### Documentation
- API documentation generation
- User guides and tutorials
- Plugin development guidelines
- Configuration reference
- Troubleshooting guides

## [Unreleased]

### Planned
- PySide6 support
- Additional plugin types
- Theme marketplace integration
- Advanced configuration templates
- Enhanced error recovery
- Performance optimizations
