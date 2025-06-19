# Contributing to Pomodoro Lock

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

Thank you for your interest in contributing to Pomodoro Lock! This document provides guidelines and information for contributors.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Project Structure](#project-structure)
4. [Areas for Contribution](#areas-for-contribution)
5. [Testing Guidelines](#testing-guidelines)
6. [Reporting Issues](#reporting-issues)
7. [Code of Conduct](#code-of-conduct)
8. [Contact Information](#contact-information)

## Getting Started

### Prerequisites
- Python 3.6 or higher
- GTK3 development libraries
- Git

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/vgundala/pomodoro-lock.git
   cd pomodoro-lock
   ```

2. **Install dependencies**
   ```bash
   # System dependencies
   sudo apt-get install python3-gi python3-psutil python3-xlib python3-notify2
   
   # Python dependencies
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   make test
   ```

## Development Workflow

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Testing
- Write tests for new features
- Ensure all existing tests pass
- Test on multiple desktop environments if possible
- Test with multiple display configurations

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**
   ```bash
   make test
   make install-desktop
   make start
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Project Structure

```
pomodoro-lock/
├── src/                    # Source code
├── scripts/                # Installation and utility scripts
├── config/                 # Configuration files
├── tests/                  # Test scripts
├── docs/                   # Documentation
├── debian/                 # Debian packaging files
├── Makefile               # Build and development commands
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── PACKAGING.md          # Packaging guide
├── CONTRIBUTING.md       # This file
└── README.md             # Project documentation
```

## Areas for Contribution

### High Priority
- Bug fixes and stability improvements
- Better error handling and logging
- Performance optimizations
- Additional desktop environment support

### Medium Priority
- New configuration options
- Additional notification types
- Statistics and reporting features
- Accessibility improvements

### Low Priority
- UI/UX improvements
- Additional themes
- Integration with other productivity tools
- Mobile companion app

## Testing Guidelines

### Manual Testing
- Test on different desktop environments (GNOME, KDE, XFCE)
- Test with single and multiple displays
- Test with different screen resolutions
- Test notification systems
- Test systemd service integration

### Automated Testing
- Unit tests for core functionality
- Integration tests for system interactions
- Mock tests for external dependencies

## Reporting Issues

When reporting issues, please include:

1. **System Information**
   - OS version and distribution
   - Desktop environment
   - Python version
   - Display configuration

2. **Steps to Reproduce**
   - Clear, step-by-step instructions
   - Expected vs actual behavior

3. **Logs and Output**
   - Service logs: `journalctl --user -u pomodoro-lock.service`
   - Application logs: `~/.local/share/pomodoro-lock/pomodoro.log`
   - Any error messages

4. **Additional Context**
   - When did the issue start?
   - Does it happen consistently?
   - Any recent system changes?

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Contact Information

### Project Maintainer
- **Author**: Vinay Gundala
- **Email**: [vg@ivdata.dev](mailto:vg@ivdata.dev)
- **GitHub**: [@vgundala](https://github.com/vgundala)

### Project Links
- **Repository**: [pomodoro-lock](https://github.com/vgundala/pomodoro-lock)
- **Issues**: [GitHub Issues](https://github.com/vgundala/pomodoro-lock/issues)
- **Documentation**: [docs/README.md](docs/README.md)

## Questions?

If you have questions about contributing, please:
1. Check the documentation in `docs/README.md`
2. Search existing issues and discussions
3. Create a new issue with the "question" label
4. Contact the maintainer directly at [vg@ivdata.dev](mailto:vg@ivdata.dev)

## License

By contributing to Pomodoro Lock, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Pomodoro Lock! 🍅 