# 🤝 Contributing to Compliance Fort

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone repository
git clone <repo>
cd compliance-fort

# Build Fortran library
make lib

# Install Python dependencies
make api

# Run tests
make test
```

## Code Style

### Fortran
- Use `implicit none`
- Follow F90/F95 standards
- Comment complex algorithms
- Use descriptive variable names

### Python
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests

## Testing

```bash
# Run all tests
make test

# Run specific test file
cd api && pytest tests/test_api.py -v
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Reporting Issues

Please include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

## Questions?

Open an issue or start a discussion!


