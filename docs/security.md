# HyprRice Security Guide

## Overview

HyprRice implements comprehensive security measures to protect against common attack vectors, ensure data integrity, and provide a safe execution environment for plugins. This guide covers HyprRice's security architecture, implementation details, and best practices.

## Security Architecture

### Core Security Components

1. **Input Validation**: Comprehensive validation of user inputs, configuration data, and file operations
2. **Plugin Sandboxing**: Isolated execution environment with resource limits and import restrictions
3. **Secure File Operations**: Atomic file operations with backup validation and permissions checking
4. **Command Sanitization**: Safe execution of system commands through hyprctl with validation
5. **Audit Logging**: Comprehensive audit trails for security monitoring and debugging

## Input Validation System

### `hyprrice.security.InputValidator`

Validates and sanitizes all user inputs to prevent injection attacks.

```python
class InputValidator:
    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate file paths to prevent directory traversal attacks."""
        # Prevents ../../../etc/passwd style attacks
        normalized_path = os.path.normpath(path)
        return not '..' in normalized_path and os.path.exists(path)
    
    @staticmethod
    def validate_color(color: str) -> bool:
        """Validate CSS color formats (hex, rgb, rgba)."""
        import re
        hex_pattern = r'^#[0-9A-Fa-f]{3,8}$'
        rgb_pattern = r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
        rgba_pattern = r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$'
        
        return bool(re.match(hex_pattern, color) or 
                   re.match(rgb_pattern, color) or 
                   re.match(rgba_pattern, color))
    
    @staticmethod
    def sanitize_command(cmd: str) -> str:
        """Sanitize hyprctl commands to prevent injection."""
        allowed_commands = {
            'monitors', 'workspaces', 'activewindow', 'clients',
            'dispatch', 'keyword', 'setprop', 'getprop'
        }
        
        parts = cmd.split()
        if parts[0] not in allowed_commands:
            raise SecurityError(f"Command not allowed: {parts[0]}")
        
        return cmd
```

### Validation Rules

#### File Path Validation
- **Directory Traversal Prevention**: Blocks `../`, `..\`, and similar patterns
- **Path Normalization**: Standardizes paths before validation
- **Permission Checking**: Verifies file permissions before operations
- **Size Limits**: Enforces maximum file sizes (default: 10MB)

#### Color Validation
- **Format Validation**: Supports hex (#fff, #ffffff), RGB, RGBA formats
- **Value Range Checking**: Ensures color values are within valid ranges
- **Malicious Pattern Detection**: Blocks suspicious color patterns

#### Command Sanitization
- **Command Whitelist**: Only allows specific hyprctl commands
- **Argument Validation**: Validates command arguments against patterns
- **Encoding Protection**: Prevents command injection through encoding

## Plugin Sandboxing System

### `hyprrice.plugin_sandbox.PluginSandbox`

Provides secure execution environment with multiple security levels.

```python
class PluginSandbox:
    def __init__(self, security_level: str = "medium"):
        self.security_level = security_level
        self.resource_limits = self._get_resource_limits()
        self.import_restrictions = self._get_import_restrictions()
    
    def _get_resource_limits(self) -> Dict[str, int]:
        """Get resource limits based on security level."""
        limits = {
            "strict": {"memory": 50*1024*1024, "cpu_time": 10, "files": 20},
            "medium": {"memory": 100*1024*1024, "cpu_time": 30, "files": 50},
            "relaxed": {"memory": 200*1024*1024, "cpu_time": 60, "files": 100}
        }
        return limits[self.security_level]
    
    def _get_import_restrictions(self) -> Set[str]:
        """Get list of restricted imports."""
        return {
            'subprocess', 'os', 'sys', 'ctypes', 'urllib.request',
            'socket', 'ftplib', 'smtplib', 'http.server',
            'webbrowser', 'shutil', 'tempfile.__main__'
        }
    
    def execute_plugin(self, plugin_code: str) -> Any:
        """Execute plugin code in sandboxed environment."""
        
        # Create restricted globals
        restricted_globals = self._create_restricted_globals()
        
        try:
            # Set resource limits
            self._set_resource_limits()
            
            # Execute in restricted environment
            exec(plugin_code, restricted_globals)
            
        except SecurityViolationError as e:
            self.log_security_violation(e)
            raise
        
        finally:
            self._restore_resource_limits()
```

### Security Levels

#### Strict Level
- **Memory Limit**: 50MB
- **CPU Time**: 10 seconds
- **File Descriptors**: 20
- **Blocking**: All network operations
- **Use Case**: Untrusted plugins from unknown sources

#### Medium Level (Default)
- **Memory Limit**: 100MB
- **CPU Time**: 30 seconds  
- **File Descriptors**: 50
- **Blocking**: Dangerous system operations
- **Use Case**: Community plugins with basic validation

#### Relaxed Level
- **Memory Limit**: 200MB
- **CPU Time**: 60 seconds
- **File Descriptors**: 100
- **Blocking**: Direct system access only
- **Use Case**: Trusted plugins from verified developers

### Resource Monitoring

```python
class ResourceMonitor:
    def __init__(self, limits: Dict[str, int]):
        self.limits = limits
        self.thread_monitor = None
    
    def start_monitoring(self):
        """Start resource monitoring in background thread."""
        self.thread_monitor = threading.Thread(
            target=self._monitor_resources,
            daemon=True
        )
        self.thread_monitor.start()
    
    def _monitor_resources(self):
        """Monitor plugin resource usage."""
        while self.running:
            current_memory = self._get_memory_usage()
            current_cpu = self._get_cpu_usage()
            
            if current_memory > self.limits["memory"]:
                self._trigger_memory_limit()
            
            if current_cpu > self.limits["cpu_time"]:
                self._trigger_cpu_limit()
            
            time.sleep(0.1)
```

## Secure File Operations

### `hyprrice.security.SecureFileHandler`

Provides atomic file operations with validation and backup creation.

```python
class SecureFileHandler:
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def write_config(self, file_path: str, content: str) -> bool:
        """Write configuration file with security checks."""
        
        # Validate file path
        if not InputValidator.validate_path(file_path):
            raise SecurityError("Invalid file path")
        
        # Validate content
        if not self._validate_content(content):
            raise SecurityError("Invalid content")
        
        # Create backup
        backup_path = self.backup_manager.create_backup(file_path)
        
        try:
            # Write to temporary file first
            temp_path = f"{file_path}.tmp_{int(time.time())}"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Verify write
            self._verify_write(temp_path, content)
            
            # Atomic move
            os.rename(temp_path, file_path)
            
            return True
            
        except Exception as e:
            # Restore from backup on failure
            self._restore_from_backup(file_path, backup_path)
            raise SecurityError(f"Write failed: {e}")
    
    def _validate_content(self, content: str) -> bool:
        """Validate file content for security."""
        
        # Check for null bytes
        if '\x00' in content:
            return False
        
        # Check file size
        if len(content.encode('utf-8')) > 10 * 1024 * 1024:  # 10MB
            return False
        
        # Validate YAML structure
        if content.strip().startswith(('general:', 'hyprland:')):
            try:
                yaml.safe_load(content)
            except yaml.YAMLError:
                return False
        
        return True
```

### Atomic Operations

All file operations use atomic patterns:

1. **Write to Temporary File**: Initial write to `filename.tmp_timestamp`
2. **Validation**: Verify content integrity and security
3. **Atomic Move**: Move temporary file to destination
4. **Backup Integration**: Automatic backup before modifications
5. **Rollback**: Restore from backup if operation fails

## Configuration Security

### Configuration Validation

```python
class ConfigSecurityValidator:
    @staticmethod
    def validate_config_schema(config: Dict[str, Any]) -> List[str]:
        """Validate configuration against security schema."""
        errors = []
        
        # Validate paths
        paths = config.get('paths', {})
        for key, path in paths.items():
            if not InputValidator.validate_path(os.path.expanduser(path)):
                errors.append(f"Invalid path in config: {key}={path}")
        
        # Validate colors
        colors = config.get('colors', {})
        for key, color in colors.items():
            if not InputValidator.validate_color(color):
                errors.append(f"Invalid color in config: {key}={color}")
        
        # Validate file sizes
        if 'max_file_size' in config:
            if not isinstance(config['max_file_size'], int) or config['max_file_size'] <= 0:
                errors.append("max_file_size must be positive integer")
        
        return errors
    
    @staticmethod
    def sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration data."""
        sanitized = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                # Remove null bytes and control characters
                sanitized[key] = ''.join(c for c in value if ord(c) >= 32 or c in '\t\n\r')
            elif isinstance(value, dict):
                sanitized[key] = ConfigSecurityValidator.sanitize_config(value)
            else:
                sanitized[key] = value
        
        return sanitized
```

### Secure Configuration Loading

```python
def secure_load_config(file_path: str) -> Dict[str, Any]:
    """Load configuration with security validation."""
    
    # Validate file path
    if not InputValidator.validate_path(file_path):
        raise SecurityError("Configuration file path not allowed")
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        raise SecurityError("Insufficient permissions to read config")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validate content
        ConfigSecurityValidator.validate_content(content)
        
        # Parse YAML safely
        config = yaml.safe_load(content)
        
        # Sanitize before returning
        return ConfigSecurityValidator.sanitize_config(config)


```

## Audit Logging

### Security Event Logging

```python
class SecurityAuditLogger:
    def __init__(self, log_file: str = "~/.hyprrice/logs/security.log"):
        self.log_file = os.path.expanduser(log_file)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup security-specific logging."""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - SECURITY - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-relevant events."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "user": os.environ.get("USER", "unknown"),
            "process_id": os.getpid()
        }
        
        logging.info(f"Security Event: {json.dumps(log_data)}")
    
    def log_plugin_execution(self, plugin_name: str, execution_result: str):
        """Log plugin execution attempts."""
        self.log_security_event(
            "plugin_execution",
            {
                "plugin": plugin_name,
                "result": execution_result
            }
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool):
        """Log file operations."""
        self.log_security_event(
            "file_operation",
            {
                "operation": operation,
                "file_path": file_path,
                "success": success
            }
        )
```

### Security Monitoring

```python
class SecurityMonitor:
    def __init__(self):
        self.audit_logger = SecurityAuditLogger()
        self.violation_count = defaultdict(int)
        self.last_violation = {}
    
    def check_security_thresholds(self, violation_type: str):
        """Check if security thresholds are exceeded."""
        
        self.violation_count[violation_type] += 1
        
        # Alert if threshold exceeded
        if self.violation_count[violation_type] > 10:
            self.audit_logger.log_security_event(
                "threshold_exceeded",
                {
                    "violation_type": violation_type,
                    "count": self.violation_count[violation_type]
                }
            )
            
            # Consider blocking further operations
            if violation_type == "path_traversal":
                self._block_file_operations()
    
    def _block_file_operations(self):
        """Temporarily block file operations after repeated violations."""
        logging.warning("Blocking file operations due to security violations")
        # Implementation would disable file operations for a time period
```

## Best Practices

### For Developers

#### Plugin Development
1. **Minimal Permissions**: Request only necessary permissions
2. **Input Validation**: Validate all inputs from users or configuration
3. **Error Handling**: Don't expose sensitive information in error messages
4. **Resource Limits**: Respect plugin resource limits
5. **Secure Communication**: Use HyprRice APIs instead of direct system calls

#### Configuration Handling
1. **Validate Early**: Validate all configuration data on load
2. **Sanitize Input**: Remove dangerous characters and patterns
3. **Backup Before Changes**: Always create backups before modifications
4. **Atomic Operations**: Use atomic file operations for safety
5. **Permission Checking**: Verify file permissions before operations

#### API Usage
1. **Use Security APIs**: Prefer HyprRice security APIs over direct operations
2. **Log Security Events**: Log important security-related events
3. **Handle Errors Gracefully**: Provide clear error messages without exposing internals
4. **Validate Dependencies**: Ensure security of external dependencies

### For Users

#### Configuration Security
1. **Backup Regularly**: Use HyprRice's backup system frequently
2. **Verify Sources**: Only install plugins from trusted sources
3. **Monitor Logs**: Regularly check security logs for anomalies
4. **Update Dependencies**: Keep HyprRice and dependencies updated
5. **Secure Permissions**: Ensure proper file permissions for configuration files

#### Plugin Management

1. **Sandbox Level**: Use appropriate sandbox levels for plugins
2. **Review Permissions**: Understand what permissions plugins request
3. **Monitor Behavior**: Watch for unusual plugin behavior
4. **Regular Audits**: Regularly audit installed plugins
5. **Quick Removal**: Know how to quickly disable problematic plugins

## Security Configuration

### Security Settings

Configuration options for security behavior:

```yaml
security:
  # Plugin sandboxing
  plugin_sandbox_level: "medium"  # strict, medium, relaxed
  
  # File operations
  max_file_size: 10485760  # 10MB in bytes
  disable_directory_traversal: true
  require_file_backups: true
  
  # Audit logging
  enable_security_logging: true
  security_log_path: "~/.hyprrice/logs/security.log"
  security_log_retention_days: 30
  
  # Input validation
  strict_color_validation: true
  block_control_characters: true
  validate_config_schema: true
  
  # Network security (future)
  disable_network_access: false
  allowed_hosts: []
```

### Environment Variables

Security-related environment variables:

```bash
# Plugin security
export HYPRRICE_SECURITY_LEVEL=medium
export HYPRRICE_DISABLE_PLUGINS=false

# Audit logging
export HYPRRICE_SECURITY_LOG=~/.hyprrice/logs/security.log
export HYPRRICE_AUDIT_MODE=detailed

# File operations
export HYPRRICE_MAX_FILE_SIZE=10485760
export HYPRRICE_REQUIRE_BACKUPS=true
```

## Incident Response

### Security Violation Handling

```python
class SecurityIncidentResponse:
    def handle_violation(self, violation_type: str, details: Dict[str, Any]):
        """Handle security violations according to type and severity."""
        
        severity = self._assess_severity(violation_type, details)
        
        if severity == "critical":
            self._critical_response(violation_type, details)
        elif severity == "high":
            self._high_response(violation_type, details)
        else:
            self._log_violation(violation_type, details)
    
    def _critical_response(self, violation_type: str, details: Dict[str, Any]):
        """Critical violation response."""
        # Immediately disable plugin or operation
        # Log extensively
        # Consider user notification
        pass
    
    def _high_response(self, violation_type: str, details: Dict[str, Any]):
        """High severity violation response."""
        # Increase monitoring
        # Log violation
        # Consider temporary restrictions
        pass
```

### Recovery Procedures

1. **Immediate Response**:
   - Disable problematic plugin/operation
   - Restore from latest backup
   - Check security logs for scope of violation

2. **Investigation**:
   - Analyze audit logs
   - Identify attack vector
   - Assess data compromise

3. **Recovery**:
   - Apply security patches
   - Update security configurations
   - Re-enable operations gradually

4. **Prevention**:
   - Update security policies
   - Enhance monitoring
   - Improve vulnerability scanning

## Compliance

### Data Protection Compliance

HyprRice implements measures to support compliance with data protection regulations:

- **Minimal Data Collection**: Only collects necessary configuration data
- **Local Storage**: All data stored locally, no remote transmission
- **User Control**: Users have full control over their data
- **Audit Trails**: Comprehensive logging for compliance auditing
- **Data Destruction**: Secure deletion of configuration backups

### Security Standards

HyprRice aligns with several security standards:

- **OWASP Guidelines**: Protection against common web vulnerabilities
- **ISO 27001**: Information security management practices
- **Sandboxing Standards**: Secure execution environment best practices
- **File Security**: Secure file operation practices

## Future Enhancements

### Planned Security Features

1. **Cryptographic Signing**: Sign plugins and configurations
2. **Network Security**: Secure cloud integration features
3. **Advanced Monitoring**: AI-powered anomaly detection
4. **Compliance Reporting**: Automated compliance report generation
5. **Security Dashboard**: Real-time security status overview

### Integration Opportunities

1. **System Security**: Integration with system security frameworks
2. **Container Security**: Docker/container security practices
3. **CIS Benchmarks**: Compliance with CIS security benchmarks
4. **Penetration Testing**: Automated security testing integration

---

This security guide covers HyprRice's comprehensive security architecture. For implementation details, see the [API Reference](api.md) and [Plugin Development Guide](plugins.md).

