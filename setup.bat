@echo off
title HealthVoice Setup Assistant (v4)
color 0A

echo ==========================================
echo      HealthVoice Setup Assistant
echo ==========================================
echo.

:CHECK_CONDA
:: Cek apakah Conda terinstall
WHERE conda >nul 2>nul
IF %ERRORLEVEL% EQU 0 GOTO CHECK_ENV

echo [INFO] Conda tidak ditemukan.
echo [INFO] Memulai download otomatis Miniconda...

:DOWNLOAD_MINICONDA
curl -o miniconda.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
IF %ERRORLEVEL% NEQ 0 GOTO ERROR_DOWNLOAD

echo [INFO] Menginstall Miniconda (Mohon tunggu, ini memakan waktu beberapa menit)...
start /wait "" miniconda.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3

del miniconda.exe

echo [INFO] Instalasi selesai. Mengkonfigurasi environment sementara...
set "PATH=%UserProfile%\Miniconda3\condabin;%PATH%"

:: Verifikasi ulang
WHERE conda >nul 2>nul
IF %ERRORLEVEL% NEQ 0 GOTO ERROR_CONDA_INSTALL

:CHECK_ENV
echo [1/4] Checking existing environment...
call conda env list | findstr healthvoice_new >nul
IF %ERRORLEVEL% EQU 0 GOTO UPDATE_ENV

echo [INFO] Environment not found. Starting installation...
call conda config --set remote_read_timeout_secs 120
call conda env remove -n healthvoice_new -y

echo [2/4] Creating environment...
call conda create -n healthvoice_new python=3.11 -y
GOTO INSTALL_LIBS

:UPDATE_ENV
echo [INFO] Environment 'healthvoice_new' already exists.
echo [INFO] Verifying and updating libraries...
call conda activate healthvoice_new
GOTO INSTALL_LIBS_FAST

:INSTALL_LIBS
echo [3/4] Installing libraries...
call conda activate healthvoice_new
python -m pip install --upgrade pip

:INSTALL_LIBS_FAST
echo Attempting fast installation via pip...
python -m pip install https://github.com/abetlen/llama-cpp-python/releases/download/v0.2.90/llama_cpp_python-0.2.90-cp311-cp311-win_amd64.whl

IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pip install failed. Switching to Conda-forge...
    call conda install -c conda-forge llama-cpp-python -y
)

echo Installing FFmpeg...
call conda install -c conda-forge ffmpeg -y

pip install -r requirements.txt

echo [4/4] Downloading AI Models...
python setup_models.py

echo ==========================================
echo      Setup Complete!
echo ==========================================
GOTO RUN

:ERROR_DOWNLOAD
color 0C
echo [ERROR] Gagal mendownload Miniconda. Cek koneksi internet.
pause
exit /b

:ERROR_CONDA_INSTALL
color 0C
echo [ERROR] Gagal memanggil Conda setelah instalasi.
echo Silakan restart komputer atau terminal Anda, lalu jalankan script ini lagi.
pause
exit /b

:RUN
echo.
echo [INFO] Starting HealthVoice Application...
echo Press Ctrl+C to stop the server.
echo.
call conda activate healthvoice_new
python app.py
pause
