echo ==========================================
echo      HealthVoice Setup Assistant (v2)
echo ==========================================

WHERE conda >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Conda tidak ditemukan!
    echo.
    echo Mohon install Miniconda terlebih dahulu agar script ini bisa berjalan.
    echo Download di: https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo Setelah install, restart terminal ini dan jalankan lagi.
    pause
    exit /b
)

echo [1/4] Checking existing environment...
call conda env list | findstr healthvoice_new >nul
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] Environment 'healthvoice_new' already exists.
    echo [INFO] Verifying and updating libraries...
    call conda activate healthvoice_new
    
    REM Ensure llama-cpp-python is installed
    python -m pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    
    REM Ensure other dependencies are installed
    pip install -r requirements.txt
    
    REM Ensure models are present
    python download_models.py
    
    goto RUN
)

echo [INFO] Environment not found. Starting installation...
call conda config --set remote_read_timeout_secs 120
REM Remove just in case it's a partial install
call conda env remove -n healthvoice_new -y

echo [2/4] Creating environment...
call conda create -n healthvoice_new python=3.11 -y

echo [3/4] Installing libraries...
call conda activate healthvoice_new
python -m pip install --upgrade pip

echo Attempting fast installation via pip...
python -m pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pip install failed. Switching to Conda-forge (slower but reliable)...
    call conda install -c conda-forge llama-cpp-python -y
)

pip install -r requirements.txt

echo [4/4] Downloading AI Models...
call conda run -n healthvoice_new python download_models.py

echo ==========================================
echo      Setup Complete!
echo ==========================================

:RUN
echo.
echo [INFO] Starting HealthVoice Application...
echo Press Ctrl+C to stop the server.
echo.
call conda activate healthvoice_new
python app.py
pause
