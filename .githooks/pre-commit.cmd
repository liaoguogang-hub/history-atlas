@echo off
rem 提交前钩子（Windows 备用入口）。Git for Windows 会优先执行同目录下的
rem 无扩展名 pre-commit（sh 脚本，由 Git 自带的 bash 执行），
rem 这里只是多一条保险路径，逻辑与 sh 版一致。
setlocal
set "HOOK_SH=%~dp0..\..\.githooks\pre-commit"
if not exist "%HOOK_SH%" exit /b 0
where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_SH%"
    exit /b %ERRORLEVEL%
)
exit /b 0
