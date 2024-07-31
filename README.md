# Testing suite using mvx python sdk and chain-simulator

## Overview:
- This repository contains the automated testing suite for MultiversX blockchain simulations. It is designed to facilitate the testing of blockchain behaviors under various scenarios using the MultiversX chain simulator.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [How to Run Tests](#how-to-run-tests)

## Installation
### Prerequisites

- Python 3.x
- pip
- git
- Access to MultiversX chain simulator

### Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv ./venv
   source ./venv/bin/activate

2. **Install Requirements:**
   - ./scripts/install-hooks.sh: This script should contain the commands to set up your Git hooks, typically something like linking or copying the **pre-commit** hooks into the **.git/hooks** directory.
    ```bash
   pip install -r ./requirements.txt && ./scripts/install-hooks.sh

   If you have already installed the Python packages separately, you can set up the Git hooks by running:

   ./scripts/git-hooks/install-hooks.sh
3. **Set environment variables:**
    ```bash
   export PYTHONPATH=.
4. **Pull and build Chain-Simulator:**
   - Please ensure Golang version: go1.20.7 is installed
   ```bash
   git pull https://github.com/multiversx/mx-chain-simulator-go.git
   go build ~/mx-chain-simulator-go/cmd/chainsimulator
   Get Path and export it to environment variable CHAIN_SIMULATOR_BUILD_PATH
   Or save it to constants.py | specific_path = os.path.expanduser("CHAIN_SIMULATOR_BINARY_PATH")

### Configure PyTest in PyCharm/IntelliJ IDEA Ultimate:
For users utilizing PyCharm or IntelliJ IDEA Ultimate, it's recommended to set up your PyTest configuration to streamline the testing process. Follow these steps to configure:
1. Navigate to **File** -> **Settings** -> **Tools** -> **Python Integrated Tools** -> **Testing**.
2. Choose **pytest** in the **Default test runner** section.
3. Go to **Run** -> **Edit Configurations**.
4. Under **Python Tests** -> **pytest autodetect**, add a new configuration template.
5. In the **Working directory** field, specify:
   **/home/python-qa/multiversX/mx-chain-testing-suite**

## How to Run Tests

- **Run all scenarios:**
  ```bash
  pytest scenarios/
- **Run a specific scenario:**
    ```bash
  pytest scenarios/_17.py
  ```

## Pre-commit Hooks Usage

Pre-commit hooks are configured to ensure code quality and style consistency. Below are key commands to manage and utilize pre-commit in your development workflow:

### Running Pre-commit Hooks

- **Manually run pre-commit on all files:**
  ```bash
  pre-commit run --all-files

- **Manually run pre-commit on staged files only:**
  ```bash
  pre-commit run

### Clearing the Pre-commit Cache

- **If you encounter issues or want to ensure fresh checks, you can clear the pre-commit cache:**
  ```bash
  pre-commit clean

### Skipping Hooks Temporarily

- **If you need to bypass the pre-commit hooks for a specific commit (use sparingly):**
  ```bash
  git commit -m "Your commit message" --no-verify

### Auto-update Hooks

- **To keep your hooks up to date with the latest versions specified in the .pre-commit-config.yaml file:**
  ```bash
  pre-commit autoupdate
