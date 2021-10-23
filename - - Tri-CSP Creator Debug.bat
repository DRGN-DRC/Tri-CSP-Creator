@echo off

python "%~dp0Tri-CSP Creator.py" gui %*

echo.
echo.

if [%ERRORLEVEL%]==[0] goto: eof

echo Error Level: %ERRORLEVEL%
echo.
echo Press any key to exit. . .
pause > nul