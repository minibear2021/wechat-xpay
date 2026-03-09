# Contributing to WeChat XPay SDK

Thank you for your interest in contributing to this project!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wechat-xpay.git
cd wechat-xpay
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wechat_xpay --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py -v
```

## Code Quality

We use `black`, `ruff`, and `mypy` for code quality:

```bash
# Format code
black .

# Lint code
ruff check . --fix

# Type check
mypy wechat_xpay
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Run code quality tools
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Reporting Issues

When reporting issues, please include:

- Python version
- SDK version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages and stack traces
