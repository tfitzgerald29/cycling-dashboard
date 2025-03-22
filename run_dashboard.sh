#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the path to your conda environment
CONDA_ENV_NAME="base"

# Detect conda installation - try different common paths
CONDA_PATHS=(
  "$HOME/opt/anaconda3/etc/profile.d/conda.sh"
  "$HOME/anaconda3/etc/profile.d/conda.sh"
  "$HOME/miniconda3/etc/profile.d/conda.sh"
  "/opt/anaconda3/etc/profile.d/conda.sh"
  "/usr/local/anaconda3/etc/profile.d/conda.sh"
  "/usr/local/miniconda3/etc/profile.d/conda.sh"
  "$HOME/.conda/etc/profile.d/conda.sh"
)

CONDA_PATH=""
for path in "${CONDA_PATHS[@]}"; do
  if [ -f "$path" ]; then
    CONDA_PATH="$path"
    break
  fi
done

if [ -z "$CONDA_PATH" ]; then
  echo "Could not find conda.sh file. Trying to use conda directly..."
  
  # Check if conda command is available
  if command -v conda > /dev/null 2>&1; then
    echo "Using conda command directly"
    # Navigate to the project directory
    cd "$SCRIPT_DIR"
    
    # Activate the conda environment and run the dashboard
    echo "Activating conda environment: $CONDA_ENV_NAME"
    conda activate "$CONDA_ENV_NAME" && python main.py
    
    # Deactivate the environment when done
    conda deactivate
    exit 0
  else
    echo "Error: Could not find conda installation."
    echo "Please make sure conda is installed and in your PATH."
    exit 1
  fi
fi

echo "Using conda from: $CONDA_PATH"

# Source the conda.sh file to make conda available
source "$CONDA_PATH"

# Navigate to the project directory
cd "$SCRIPT_DIR"

# Activate the conda environment and run the dashboard
echo "Activating conda environment: $CONDA_ENV_NAME"
conda activate "$CONDA_ENV_NAME" && python main.py

# Deactivate the environment when done
conda deactivate 