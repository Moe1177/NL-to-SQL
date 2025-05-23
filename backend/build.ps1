$PYTHON_VERSION = "3.11.8"

function Create-DataLink {
    param (
        [string]$Path,
        [string]$Shortcut
    )
    New-Item -ItemType SymbolicLink -Path $Shortcut -Target $Path
}

function Setup-Environment {
    Write-Host "Setting up Python environment..." -ForegroundColor Green
    
    # Check if Python is installed
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Python not found. Please install Python $PYTHON_VERSION from python.org" -ForegroundColor Red
        exit 1
    }
    
    # Check if Poetry is installed
    if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Poetry..." -ForegroundColor Yellow
        python -m pip install --upgrade pip
        pip install poetry==1.8.5
    }
    
    # Configure Poetry to create virtual environment in project directory
    Write-Host "Configuring Poetry..." -ForegroundColor Yellow
    poetry config virtualenvs.in-project true
    
    # Install dependencies using Poetry
    Write-Host "Installing dependencies with Poetry..." -ForegroundColor Yellow
    poetry install --with dev
    
    Write-Host "Environment setup complete!" -ForegroundColor Green
    Write-Host "To activate the environment, run: poetry shell" -ForegroundColor Cyan
}

function Update-Lock {
    Write-Host "Updating lock file..." -ForegroundColor Yellow
    poetry lock
    Write-Host "Lock file updated!" -ForegroundColor Green
}

function Update-Environment {
    Write-Host "Updating environment..." -ForegroundColor Yellow
    poetry install --no-root --all-extras --with dev,test,code-quality,notebook
    Write-Host "Environment updated!" -ForegroundColor Green
}

function Clean-Project {
    Write-Host "Cleaning project files..." -ForegroundColor Yellow
    
    # Remove pycache files
    Get-ChildItem -Path . -Include *.pyc -Recurse | Remove-Item
    Get-ChildItem -Path . -Include __pycache__ -Directory -Recurse | Remove-Item -Recurse
    
    # Remove egg-info directories
    Get-ChildItem -Path . -Include *.egg-info -Directory -Recurse | Remove-Item -Recurse
    
    # Remove coverage files
    if (Test-Path .coverage) {
        Remove-Item .coverage
    }
    
    Write-Host "Project cleaned!" -ForegroundColor Green
}

# Handle command line arguments
$command = $args[0]

switch ($command) {
    "datalink" {
        if ($args.Length -lt 3) {
            Write-Host "Usage: .\build.ps1 datalink [PATH] [SHORTCUT]" -ForegroundColor Red
        } else {
            Create-DataLink -Path $args[1] -Shortcut $args[2]
        }
    }
    "env" {
        Setup-Environment
    }
    "update-lock" {
        Update-Lock
    }
    "update-env" {
        Update-Environment
    }
    "clean" {
        Clean-Project
    }
    default {
        Write-Host "FastAPI Backend Build Script" -ForegroundColor Cyan
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  datalink [PATH] [SHORTCUT] - Create a symbolic link"
        Write-Host "  env                        - Set up Python environment"
        Write-Host "  update-lock                - Update lock file"
        Write-Host "  update-env                 - Update environment packages"
        Write-Host "  clean                      - Clean project files"
    }
} 
