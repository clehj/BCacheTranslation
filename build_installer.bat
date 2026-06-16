@echo off
chcp 65001 >nul
echo ========================================
echo   BCacheTranslation 安装包制作工具
echo ========================================
echo.

echo [1/3] 检查文件...
if not exist "dist\BCacheTranslation_v2.0.0\BCacheTranslation_v2.0.0.exe" (
    echo 错误: 找不到 BCacheTranslation_v2.0.0.exe，请先运行打包
    pause
    exit /b 1
)

echo [2/3] 复制许可证文件...
if not exist "LICENSE.txt" (
    copy LICENSE MIT_LICENSE
)

echo [3/3] 编译安装脚本...
"D:\Program Files\Inno Setup 6\ISCC.exe" installer.iss

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   安装包制作成功！
    echo   输出目录: installer\
    echo ========================================
) else (
    echo.
    echo 制作失败
)

pause