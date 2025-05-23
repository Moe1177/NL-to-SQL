# FastAPI Backend

A Python FastAPI backend application with automated environment setup and code quality tools.

## Prerequisites

- **Python 3.11.8** (recommended)
- **Git** for version control
- **Poetry** for dependency management (will be installed during setup)

## Platform-Specific Setup

### 🍎 macOS Setup

1. **Install pyenv** (if not already installed):

   ```bash
   brew install pyenv pyenv-virtualenv
   ```

2. **Configure your shell** (add to `~/.zshrc` or `~/.bash_profile`):

   ```bash
   export PATH="$HOME/.pyenv/bin:$PATH"
   eval "$(pyenv init --path)"
   eval "$(pyenv virtualenv-init -)"
   ```

3. **Set up the environment**:

   ```bash
   cd backend
   make env
   ```

4. **Available Make commands**:
   ```bash
   make env          # Set up Python environment
   make update-lock  # Update lock file
   make update-env   # Update environment packages
   make clean        # Clean project files
   ```

### 🪟 Windows Setup

1. **Install Python 3.11.8** from [python.org](https://python.org)

2. **Open PowerShell** and navigate to the backend directory:

   ```powershell
   cd "path\to\your\project\backend"
   ```

3. **Set execution policy** (if needed):

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Set up the environment**:

   ```powershell
   .\build.ps1 env
   ```

5. **Available PowerShell commands**:
   ```powershell
   .\build.ps1 env           # Set up Python environment
   .\build.ps1 update-lock   # Update lock file
   .\build.ps1 update-env    # Update environment packages
   .\build.ps1 clean         # Clean project files
   ```

## Development Workflow

### 1. Activate Virtual Environment

**macOS/Linux:**

```bash
source .venv/bin/activate
# or
poetry shell
```

**Windows:**

```powershell
.\.venv\Scripts\Activate.ps1
# or
poetry shell
```

### 2. Install Pre-commit Hooks

After setting up your environment, install pre-commit hooks for code quality:

```bash
poetry run pre-commit install
```

The pre-commit hooks will automatically run:

- **Black** - Code formatting
- **Flake8** - Style checking
- **isort** - Import sorting
- **Various file checks** - JSON, YAML, etc.

### 3. Running the Application

```bash
poetry run uvicorn app.main:app --reload
```

### 4. Adding Dependencies

**Regular dependencies:**

```bash
poetry add package-name
```

**Development dependencies:**

```bash
poetry add --group dev package-name
```

## Project Structure

```
backend/
├── app/                 # Main application code
├── tests/              # Test files (when created)
├── .venv/              # Virtual environment (created during setup)
├── pyproject.toml      # Poetry configuration and dependencies
├── poetry.lock         # Locked dependency versions
├── pre-commit.yaml     # Code quality hooks configuration
├── Makefile            # macOS/Linux build commands
├── build.ps1           # Windows build script
└── README.md           # This file
```

## Troubleshooting

### Common Issues

**Windows PowerShell execution errors:**

- Make sure you've set the execution policy (see Windows setup step 3)
- Use PowerShell, not Git Bash or Command Prompt

**macOS pyenv issues:**

- Ensure you've restarted your terminal after installing pyenv
- Verify pyenv is in your PATH: `which pyenv`

**Poetry not found:**

- The setup scripts install Poetry automatically
- If still not found, manually install: `pip install poetry==1.8.5`

**Pre-commit hooks failing:**

- Ensure your code follows Black formatting: `poetry run black .`
- Check for linting issues: `poetry run flake8`
- Sort imports: `poetry run isort .`

### Getting Help

1. Check that you're using the correct Python version: `python --version`
2. Verify Poetry is installed: `poetry --version`
3. Ensure you're in the correct directory (`backend/`)
4. Try cleaning and rebuilding: run the `clean` command then `env` command

## Contributing

1. Fork the repository
2. Set up your development environment using the instructions above
3. Create a feature branch: `git checkout -b feature-name`
4. Make your changes and ensure pre-commit hooks pass
5. Commit your changes: `git commit -m "Description of changes"`
6. Push to your fork: `git push origin feature-name`
7. Create a pull request

## License

[Add your license information here]
