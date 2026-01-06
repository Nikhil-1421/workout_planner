# Contributing to IronLog

Thank you for your interest in contributing to IronLog! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- A code editor (VS Code recommended)

### Local Development

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/workout-tracker.git
   cd workout-tracker
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Install pre-commit hooks** (optional but recommended)

   ```bash
   pre-commit install
   ```

## Code Style

We use the following tools to maintain code quality:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing

### Running Quality Checks

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app/

# Test
pytest
```

Or use the provided scripts:

```bash
./scripts/lint.sh
./scripts/test.sh
```

## Project Structure

```
app/
├── ui/          # User interface (Toga widgets)
├── core/        # Business logic (timer, models, export)
└── data/        # Data persistence (SQLite, repositories)
```

### Architecture Guidelines

1. **UI Layer** (`app/ui/`)
   - Only UI logic and widget management
   - No direct database access
   - Use repositories for data operations

2. **Core Layer** (`app/core/`)
   - Business logic and domain models
   - No UI dependencies
   - No direct database access

3. **Data Layer** (`app/data/`)
   - Database operations
   - Repository pattern for data access
   - Migration management

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(templates): add duplicate template functionality
fix(timer): correct background timer drift
docs(readme): add iOS deployment instructions
```

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run all quality checks
4. Update documentation if needed
5. Submit a PR with a clear description

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_timer.py

# Verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive names that explain what's being tested

Example:

```python
def test_timer_starts_at_zero():
    timer = Timer()
    assert timer.elapsed_seconds == 0

def test_timer_pauses_correctly():
    timer = Timer()
    timer.start()
    timer.pause()
    assert timer.is_paused
```

## UI Guidelines

### Design Principles

1. **Dark theme only** - No light mode
2. **Minimal** - Remove anything unnecessary
3. **Large tap targets** - 44pt minimum
4. **High contrast** - Readability first
5. **One primary action** - Per screen

### Color Palette

Use the theme constants from `app/ui/theme.py`:

```python
from app.ui.theme import Theme

background = Theme.BACKGROUND
primary = Theme.PRIMARY
text = Theme.TEXT
```

## Questions?

If you have questions, please:

1. Check existing issues
2. Open a new issue with the `question` label
3. Be specific and provide context

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
