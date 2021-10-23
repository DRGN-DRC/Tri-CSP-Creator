@echo off
cls

echo. & echo.
echo Are you sure you'd like to compile (y/n)?

set /p confirmation=

echo. & echo.
if [%confirmation%]==[y] (
    python setup.py build
) else (
    goto:error
)

echo. & echo.
echo Exit Code: %ERRORLEVEL%



echo.
echo      Build complete!  Press any key to exit.
pause > nul
goto: eof


:error
echo.
echo      An error has occurred. Press any key to exit.
pause > nul