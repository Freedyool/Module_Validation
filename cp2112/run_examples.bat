@echo off
rem CP2112 Pythonʾ�������ű�
rem �Զ����û���������ʾ������

title CP2112 Pythonʾ������

echo ========================================
echo    CP2112 USB�Ž��� Pythonʾ������
echo ========================================
echo.

rem ���Python�Ƿ����
python --version >nul 2>&1
if errorlevel 1 (
    echo ����: δ�ҵ�Python����
    echo ��ȷ���Ѱ�װPython 3.6����߰汾
    pause
    exit /b 1
)

rem ��ʾPython�汾
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ��ǰPython�汾: %PYTHON_VERSION%
echo.

rem �л����ű�Ŀ¼
cd /d "%~dp0"

:menu
echo ��ѡ��Ҫ���е�ʾ��:
echo.
echo 1. �豸��� - ������ӵ�CP2112�豸
echo 2. I2C����ɨ�� - ɨ��I2C�����ϵ��豸
echo 3. INA226��Դ��� - ʵʱ����ѹ��������
echo 4. �鿴README�ĵ�
echo 5. �˳�
echo.
set /p choice=������ѡ�� (1-5): 

if "%choice%"=="1" goto device_detect
if "%choice%"=="2" goto i2c_scan  
if "%choice%"=="3" goto ina226_monitor
if "%choice%"=="4" goto show_readme
if "%choice%"=="5" goto exit
echo ��Чѡ������������
goto menu

:device_detect
echo.
echo ���������豸��⹤��...
echo ========================================
python example_device_detect.py
echo ========================================
echo.
pause
goto menu

:i2c_scan
echo.
echo ��������I2C����ɨ�蹤��...
echo ========================================
python example_i2c_scan.py
echo ========================================
echo.
pause
goto menu

:ina226_monitor
echo.
echo ��������INA226��Դ��⹤��...
echo ========================================
python example_ina226_monitor.py
echo ========================================
echo.
pause
goto menu

:show_readme
echo.
echo ���ڴ�README�ĵ�...
start notepad README.md
goto menu

:exit
echo.
echo ��лʹ��CP2112 Pythonʾ�����ߣ�
echo.
pause
exit /b 0
