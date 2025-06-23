# HyprRice Style Guide

## Documentation Style

- Use Markdown for all documentation files.
- Start each doc with a top-level heading (`# Title`).
- Use second-level headings (`##`) for major sections.
- Use bullet points for lists, numbered lists for steps.
- Use fenced code blocks for code and commands.
- Reference files and classes as `filename.py`, `ClassName`.
- Use relative links for docs and images.
- Add a Table of Contents for docs longer than 2 pages.
- Use screenshots in `docs/screenshots/` and reference them inline.
- Cross-link related docs for easy navigation.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use type hints for all functions and methods.
- Use Google-style docstrings for all public functions/classes.
- Keep functions focused and small.
- Use descriptive variable and function names.
- Group imports: standard library, third-party, local.
- Use `snake_case` for variables/functions, `CamelCase` for classes.
- Document exceptions and side effects.

## Naming Conventions

- Files: `lowercase_with_underscores.py`
- Classes: `CamelCase`
- Functions/variables: `snake_case`
- Constants: `UPPERCASE`

## Example Docstring

```python
from typing import Dict, Any

def process_config(config: Dict[str, Any]) -> bool:
    """
    Process and validate configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(config, dict):
        return False
    return True
```

## Screenshot Guidelines

- Save images in `docs/screenshots/`.
- Use descriptive filenames (e.g., `main_window.png`).
- Reference with `![Alt text](../screenshots/main_window.png)`.
- Add captions below screenshots if needed.

## Markdown Example

````markdown
# Section Title

## Subsection

- Use bullet points for lists.
- Use fenced code blocks for code.
- Reference files as `filename.py`.
- Use relative links for docs.
````

## Pull Requests & Reviews

- Ensure all new code and docs follow this style guide.
- Reviewers should check for style, clarity, and consistency.
- Update this guide as the project evolves. 