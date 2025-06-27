@echo off
rem CP2112 Python示例启动脚本
rem 自动设置环境并运行示例程序

title CP2112 Python示例工具

echo ========================================
echo    CP2112 USB桥接器 Python示例工具
echo ========================================
echo.

rem 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请确保已安装Python 3.6或更高版本
    pause
    exit /b 1
)

rem 显示Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 当前Python版本: %PYTHON_VERSION%
echo.

rem 切换到脚本目录
cd /d "%~dp0"

:menu
echo 请选择要运行的示例:
echo.
echo 1. 设备检测 - 检测连接的CP2112设备
echo 2. I2C总线扫描 - 扫描I2C总线上的设备
echo 3. INA226电源监测 - 实时监测电压电流功率
echo 4. 查看README文档
echo 5. 退出
echo.
set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" goto device_detect
if "%choice%"=="2" goto i2c_scan  
if "%choice%"=="3" goto ina226_monitor
if "%choice%"=="4" goto show_readme
if "%choice%"=="5" goto exit
echo 无效选择，请重新输入
goto menu

:device_detect
echo.
echo 正在启动设备检测工具...
echo ========================================
python example_device_detect.py
echo ========================================
echo.
pause
goto menu

:i2c_scan
echo.
echo 正在启动I2C总线扫描工具...
echo ========================================
python example_i2c_scan.py
echo ========================================
echo.
pause
goto menu

:ina226_monitor
echo.
echo 正在启动INA226电源监测工具...
echo ========================================
python example_ina226_monitor.py
echo ========================================
echo.
pause
goto menu

:show_readme
echo.
echo 正在打开README文档...
start notepad README.md
goto menu

:exit
echo.
echo 感谢使用CP2112 Python示例工具！
echo.
pause
exit /b 0
