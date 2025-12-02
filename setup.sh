#!/bin/bash

# HealthVoice Setup Assistant (macOS) v4

# Set terminal title
echo -n -e "\033]0;HealthVoice Setup Assistant (v4)\007"

echo "=========================================="
echo "     HealthVoice Setup Assistant"
echo "=========================================="
echo ""

# Check if Conda is installed
if ! command -v conda &> /dev/null; then
    echo "[INFO] Conda not found."
    echo "[INFO] Starting automatic Miniconda download..."

    # Detect Architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    elif [ "$ARCH" = "arm64" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
    else
        echo "[ERROR] Unsupported architecture: $ARCH"
        exit 1
    fi

    echo "[INFO] Downloading Miniconda for $ARCH..."
    curl -o miniconda.sh "$MINICONDA_URL"
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to download Miniconda. Check internet connection."
        exit 1
    fi

    echo "[INFO] Installing Miniconda (This may take a few minutes)..."
    bash miniconda.sh -b -p "$HOME/miniconda3"
    rm miniconda.sh

    echo "[INFO] Installation complete. Configuring temporary environment..."
    export PATH="$HOME/miniconda3/bin:$PATH"
    
    # Initialize conda for this shell session
    eval "$("$HOME/miniconda3/bin/conda" shell.bash hook)"
else
    # Initialize conda for this shell session if already installed
    eval "$(conda shell.bash hook)"
fi

# Verify Conda
if ! command -v conda &> /dev/null; then
    echo "[ERROR] Failed to initialize Conda."
    echo "Please restart your terminal and try again."
    exit 1
fi

echo "[1/4] Checking existing environment..."
if conda env list | grep -q "healthvoice_new"; then
    echo "[INFO] Environment 'healthvoice_new' already exists."
    echo "[INFO] Verifying and updating libraries..."
    conda activate healthvoice_new
else
    echo "[INFO] Environment not found. Starting installation..."
    conda config --set remote_read_timeout_secs 120
    
    # Remove if exists (just in case)
    conda env remove -n healthvoice_new -y &> /dev/null
    
    echo "[2/4] Creating environment..."
    conda create -n healthvoice_new python=3.11 -y
    conda activate healthvoice_new
fi

echo "[3/4] Installing libraries..."
python -m pip install --upgrade pip

echo "Attempting installation via pip..."
# On Mac, we don't use the Windows wheel.
# We try to install with Metal support if on arm64, otherwise standard.
if [ "$(uname -m)" = "arm64" ]; then
    echo "Detected Apple Silicon. Attempting to install llama-cpp-python with Metal support..."
    # We try to install the same version as Windows for consistency, but allow build from source
    CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90 --no-cache-dir
else
    pip install llama-cpp-python==0.2.90
fi

if [ $? -ne 0 ]; then
    echo "[WARNING] Pip install failed. Switching to Conda-forge..."
    conda install -c conda-forge llama-cpp-python -y
fi

echo "Installing FFmpeg..."
conda install -c conda-forge ffmpeg -y

echo "Installing requirements..."
pip install -r requirements.txt

echo "[4/4] Downloading AI Models..."
python setup_models.py

echo "=========================================="
echo "     Setup Complete!"
echo "=========================================="

echo ""
echo "[INFO] Starting HealthVoice Application..."
echo "Press Ctrl+C to stop the server."
echo ""

python app.py
