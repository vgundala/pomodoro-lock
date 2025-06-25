# GitHub Actions for Pomodoro Lock

This project uses GitHub Actions to automatically build and release packages when you create a new version tag.

## How It Works

1. **Automatic Triggers:**
   - When you push a tag starting with `v*` (e.g., `v1.3.7`)
   - When you create a pull request
   - Manual trigger via GitHub Actions UI

2. **Build Process:**
   - **Debian Package**: Builds `.deb` package for Ubuntu/Debian systems
   - **Windows Executable**: Builds `.exe` file for Windows systems
   - **Release**: Creates GitHub release with both packages attached

## Usage

### Creating a Release

1. **Update version** in your code (if needed)
2. **Commit and push** your changes
3. **Create a release**:
   ```bash
   git tag v1.3.8
   git push origin v1.3.8
   ```
   This will:
   - Push the tag to GitHub
   - Trigger the build workflow
   - Create a GitHub release with packages

### Manual Testing

Test the build process locally:
```bash
# Test Debian package build
dpkg-buildpackage -b -us -uc

# Test Windows executable build (requires Windows or Wine)
pip install pyinstaller
pyinstaller pomodoro-lock.spec
```

## Workflow Files

- **`.github/workflows/build.yml`**: Main build and release workflow
  - Builds Debian package on Ubuntu
  - Builds Windows executable on Windows
  - Creates GitHub release with artifacts
- **`.github/workflows/test.yml`**: Test workflow for pull requests
  - Runs CI tests
  - Tests Python package build
  - Tests Debian package build

## Package Outputs

The workflows will create:

### Debian Package
- `pomodoro-lock_x.y.z-1_all.deb` (Debian package for system-wide installation)

### Windows Executable
- `pomodoro-lock.exe` (Standalone Windows executable)

## Requirements

- GitHub repository with Actions enabled
- Proper `debian/` directory for Debian packaging
- `pomodoro-lock.spec` file for PyInstaller Windows build
- Version tags following semantic versioning (e.g., `v1.3.7`)

## Installation Methods

### Linux (Debian/Ubuntu)
```bash
# Download the .deb file from GitHub releases
sudo dpkg -i pomodoro-lock_x.y.z-1_all.deb

# Or install manually
sudo ./scripts/install.sh
```

### Windows
```bash
# Download the .exe file from GitHub releases
# Run pomodoro-lock.exe directly
```

## Troubleshooting

### Build Fails
1. Check the Actions tab in your GitHub repository
2. Review the build logs for specific errors
3. Test locally with `dpkg-buildpackage -b -us -uc`

### Release Not Created
1. Ensure the tag starts with `v` (e.g., `v1.3.7`)
2. Check that the workflow completed successfully
3. Verify GitHub token permissions

### Package Issues
1. Review `debian/` files for Debian package configuration
2. Review `pomodoro-lock.spec` for Windows executable configuration
3. Test packaging locally before creating a release

### Windows Build Issues
1. Check PyInstaller configuration in `pomodoro-lock.spec`
2. Verify all dependencies are included
3. Test the executable on a clean Windows system

## Workflow Details

### Build Workflow (build.yml)
- **Ubuntu Job**: Builds Debian package with system dependencies
- **Windows Job**: Builds executable with PyInstaller
- **Release Job**: Creates GitHub release with both artifacts

### Test Workflow (test.yml)
- Runs CI tests (`tests/test-ci.py`)
- Tests Python package build
- Tests Debian package build
- Runs on pull requests to main/master

## Customization

You can modify the workflows to:
- Add more Linux distributions
- Include additional Windows configurations
- Add testing steps
- Customize release notes
- Add deployment to package repositories

## Manual Workflow Trigger

To manually trigger the build workflow:
1. Go to GitHub → Actions → Build Packages
2. Click "Run workflow"
3. Select branch (usually `main`)
4. Click "Run workflow"

This will build both Debian and Windows packages without creating a release.

See the GitHub Actions documentation for more details: https://docs.github.com/en/actions 