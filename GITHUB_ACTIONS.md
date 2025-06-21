# GitHub Actions for Pomodoro Lock

This project uses GitHub Actions to automatically build and release packages when you create a new version tag.

## How It Works

1. **Automatic Triggers:**
   - When you push a tag starting with `v*` (e.g., `v1.0.0`)
   - When you create a pull request
   - Manual trigger via GitHub Actions UI

2. **Build Process:**
   - **Python Package**: Builds wheel and source distribution for multiple Python versions
   - **Debian Package**: Builds `.deb` package for Ubuntu/Debian systems
   - **Release**: Creates GitHub release with all packages attached

## Usage

### Creating a Release

1. **Update version** in your code (if needed)
2. **Commit and push** your changes
3. **Create a release**:
   ```bash
   make github-release VERSION=1.0.0
   ```
   This will:
   - Create a git tag `v1.0.0`
   - Push the tag to GitHub
   - Trigger the build workflow
   - Create a GitHub release with packages

### Manual Testing

Test the build process locally:
```bash
make github-test
```

Or build packages manually:
```bash
make package-pip
make package-deb
```

## Workflow Files

- **`.github/workflows/build.yml`**: Main build and release workflow
- **`.github/workflows/test.yml`**: Simple test workflow for pull requests

## Package Outputs

The workflows will create:

### Python Package (pip)
- `pomodoro-lock-x.y.z.tar.gz` (source distribution)
- `pomodoro_lock-x.y.z-py3-none-any.whl` (wheel distribution)

### Debian Package
- `pomodoro-lock_x.y.z-1_all.deb` (Debian package)

### AppImage
- `Pomodoro_Lock-x.y.z-x86_64.AppImage` (AppImage for Linux)

## Requirements

- GitHub repository with Actions enabled
- Proper `setup.py` for Python packaging
- Proper `debian/` directory for Debian packaging
- Version tags following semantic versioning (e.g., `v1.0.0`)

## Troubleshooting

### Build Fails
1. Check the Actions tab in your GitHub repository
2. Review the build logs for specific errors
3. Test locally with `make package-pip` and `make package-deb`

### Release Not Created
1. Ensure the tag starts with `v` (e.g., `v1.0.0`)
2. Check that the workflow completed successfully
3. Verify GitHub token permissions

### Package Issues
1. Review `setup.py` for Python package configuration
2. Review `debian/` files for Debian package configuration
3. Test packaging locally before creating a release

## Customization

You can modify the workflows to:
- Add more Python versions
- Include additional package formats
- Add testing steps
- Customize release notes
- Add deployment to package repositories

See the GitHub Actions documentation for more details: https://docs.github.com/en/actions 