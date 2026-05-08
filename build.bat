@echo off
setlocal

rem ============================================================
rem build.bat - Gera o executavel PomodoroTimer.exe
rem ============================================================

echo [1/3] Preparando ambiente de build...
cd /d "%~dp0"

set "DIST_ROOT=C:\tmp\PomodoroTimer_dist"
set "WORK_ROOT=C:\tmp\PomodoroTimer_build"

rem Limpa artefatos de builds anteriores. A distribuicao final fica fora do
rem Google Drive porque a pasta sincronizada esta bloqueando a criacao do .exe.
if exist "build" rmdir /s /q "build"
if exist "%WORK_ROOT%" rmdir /s /q "%WORK_ROOT%"
if exist "%DIST_ROOT%" rmdir /s /q "%DIST_ROOT%"
if exist "PomodoroTimer.spec" del /q "PomodoroTimer.spec"

if exist "%DIST_ROOT%" (
    echo.
    echo ERRO: Nao foi possivel limpar %DIST_ROOT%.
    echo Feche o PomodoroTimer.exe e qualquer janela usando essa pasta, depois rode o build novamente.
    exit /b 1
)

echo [2/3] Rodando PyInstaller...

python -m PyInstaller -y ^
  --onedir ^
  --windowed ^
  --distpath "%DIST_ROOT%" ^
  --workpath "%WORK_ROOT%" ^
  --name PomodoroTimer ^
  --icon=assets\icon.png ^
  --add-data "assets;assets" ^
  --hidden-import PyQt6.QtCore ^
  --hidden-import PyQt6.QtGui ^
  --hidden-import PyQt6.QtSvg ^
  --hidden-import PyQt6.QtWidgets ^
  --hidden-import PyQt6.sip ^
  main.py

if errorlevel 1 (
    echo.
    echo ERRO: PyInstaller falhou. O executavel final nao foi atualizado.
    exit /b 1
)

if not exist "%DIST_ROOT%\PomodoroTimer\PomodoroTimer.exe" (
    echo.
    echo ERRO: Build terminou, mas o executavel final nao foi encontrado.
    exit /b 1
)

echo [3/3] Build concluido!
echo.
echo Executavel disponivel em: %DIST_ROOT%\PomodoroTimer\PomodoroTimer.exe
echo.
