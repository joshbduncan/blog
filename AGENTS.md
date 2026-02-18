# AGENTS.md - Coding Agent Guide

This guide provides essential information for AI coding agents working in this repository.

## Project Overview

**Type:** Personal blog using Flask + Flask-FlatPages (freezes to static site)  
**Tech Stack:** Python 3.13+, Flask 3.1, Jinja2, Markdown, Pygments  
**Build Tool:** uv (modern Python package manager)  
**Deployment:** Static site generation via custom Frozen-Flask implementation

## Quick Commands

### Development
```bash
make server          # Run dev server (http://localhost:5000)
make shell           # Open Flask shell
make build           # Freeze to static files (output: ../build)
make test-freeze     # Build and test frozen site locally
make imgspecs        # Get image dimensions for static images
```

### Alternative Commands (without make)
```bash
uv run flask run            # Dev server
uv run python blog.py --build   # Build static site
uv run python blog.py --run     # Test frozen site
```

### Linting & Type Checking
```bash
uv run ruff check .         # Lint with ruff
uv run ruff format .        # Format with ruff
uv run pyright              # Type check with pyright
uv run mypy .               # Type check with mypy
```

**Note:** This project does not have automated tests. Manual testing via dev server is required.

## Code Style Guidelines

### Python Style

**General:**
- Python 3.13+ required
- Max line length: 88 characters (Black/Ruff standard)
- Use type hints on all function signatures
- Use modern Python features (match/case, f-strings, pathlib, etc.)

**Formatting:**
- Tool: Ruff (replaces Black + isort)
- Config: `.flake8` (max-line-length: 88, extend-ignore: E203)
- Follow PEP 8 with Ruff's defaults

**Imports:**
- Standard library imports first
- Third-party imports second
- Local imports last
- Blank line between groups
- Absolute imports for app modules (e.g., `from app import flatpages`)
- Use `# type: ignore` for untyped third-party libraries (e.g., Flask-FlatPages)

**Example:**
```python
import os
from datetime import datetime
from pathlib import Path

from flask import render_template, url_for
from flask_flatpages import Page  # type: ignore

from app import app, flatpages
```

**Type Hints:**
- Always type function parameters and return values
- Use modern type syntax: `list[str]`, `dict[str, int]` (not `List[str]`, `Dict[str, int]`)
- Use `str | None` instead of `Optional[str]`
- Add assertions after type guards when needed for type checker satisfaction

**Example:**
```python
def get_post_tags(post: Page) -> list[str]:
    tags: str = post.meta.get("tags", "")
    return sorted(tags.split(", "))

def send_file_safely(directory: str | None) -> Response:
    if directory is None:
        abort(404)
    assert directory is not None  # for type checker
    return send_from_directory(directory, filename)
```

**Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: prefix with `_`
- Type variables: `T`, `KT`, `VT`, etc.

**Error Handling:**
- Use Flask's `abort(404)` for not-found errors
- Add custom error handlers via `@app.errorhandler(404)`
- Validate data before processing (e.g., check directory existence)
- Use assertions for type narrowing after guards

**Comments & Docstrings:**
- Use docstrings for public functions (Google style preferred)
- Inline comments for complex logic only
- Section headers with `#` for grouping routes/functions

**Example:**
```python
def get_rss_pubdate(date: datetime | None = None) -> str:
    """Format a datetime object to RFC-822 format for an RSS `pubDate`.

    Args:
        date (datetime | None): The datetime to format. Defaults to current time.

    Returns:
        str: RFC-822-compliant date string.
    """
```

### Flask-Specific Patterns

**Configuration:**
- All config in `app/config.py` as `Config` class
- Environment variables via `.env` file (python-dotenv)
- Access via `app.config.get("KEY")`

**Routes:**
- All routes in `app/routes.py`
- Group by functionality with section comments
- Use type hints on parameters and return values
- Register freezer generators with `@freezer.register_generator`

**Templates:**
- Jinja2 templates in `app/templates/`
- Pass context via `render_template("template.html", var=value)`
- Custom filters via `app.add_template_filter(func)`

**Static Files:**
- Located in `app/static/`
- Images: `app/static/images/`
- Styles: `app/static/css/`
- Downloads: `app/static/downloads/`

### Markdown Content

**Frontmatter (YAML):**
```yaml
title: Post Title
date: 2024-01-01
updated: 2024-01-15  # optional
description: Brief description for RSS/meta
author: Josh Duncan
category: programming
tags: python, flask, web
```

**Custom Extensions:**
- Callout boxes: Use `<<< .class-name >>> content >>>`
- Code blocks: Use fenced blocks with language (e.g., ```python)
- Tables: Standard Markdown tables supported
- Attributes: Use `{: .class #id }` syntax

## Project Structure

```
blog/
├── app/                        # Flask application
│   ├── flask_frozen/          # Custom Frozen-Flask (626 lines)
│   ├── markdown_div/          # Custom <div> markdown extension
│   ├── static/                # CSS, images, downloads
│   ├── templates/             # Jinja2 HTML templates
│   ├── __init__.py            # App initialization
│   ├── config.py              # Configuration
│   └── routes.py              # All routes (499 lines)
├── content/                   # Markdown content
│   ├── posts/                 # Published posts
│   └── pages/                 # Static pages (about, software)
├── blog.py                    # Entry point
├── Makefile                   # Development commands
├── pyproject.toml             # Project config (uv)
├── requirements.txt           # Pinned dependencies
└── .env                       # Environment variables
```

## Important Notes for Agents

1. **No Tests:** This project has no test suite. Validate changes by running dev server.
2. **Build Process:** Changes to routes/templates require rebuild (`make build`) to test frozen output.
4. **Custom Freezer:** Uses custom `flask_frozen` implementation, not the PyPI package.
5. **RSS/Sitemap:** Auto-generated from live posts. Ensure all links are absolute URLs.
6. **Environment:** Always use `uv run` prefix for commands to ensure correct venv.
7. **Type Checking:** Run both `pyright` and `mypy` as they catch different issues.

## Common Tasks

**Add a new route:**
1. Add route function in `app/routes.py` under appropriate section
2. Register freezer generator if route has parameters
3. Test with `make server`
4. Build and verify with `make test-freeze`

**Add a blog post:**
1. Create `content/posts/post-name.md` with YAML frontmatter
2. Write content using Markdown
3. Preview at `http://localhost:5000/post-name.html`
4. Build for production with `make build`

**Modify templates:**
1. Edit Jinja2 files in `app/templates/`
2. Test changes with `make server`
3. Check frozen output with `make test-freeze`

**Update styles:**
1. Edit CSS in `app/static/css/`
2. No build step needed for CSS
3. Hard refresh browser to see changes

## Deployment Workflow

1. Make changes and test with `make server`
2. Build static site with `make build`
3. Static files output to `../build` directory
4. Deployment target: Render (see `make render`)

---

**Last Updated:** 2025-01-22  
**For questions:** See `/content/pages/about.md` for contact info
