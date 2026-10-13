@echo off
chcp 65001 >nul
echo 正在編譯 EPUB 簡繁轉換器為單一 EXE 檔案...
cd /d "%~dp0"
uv run --with pyinstaller --with opencc pyinstaller --onefile --name "epub-to-traditional" --icon "icon.ico" --collect-all opencc epub_s2t.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo 編譯完成！正在複製到桌面...
    copy /y "dist\epub-to-traditional.exe" "%USERPROFILE%\Desktop\epub-to-traditional.exe"
    echo 已更新桌面上的 epub-to-traditional.exe！
) else (
    echo.
    echo [錯誤] 編譯失敗！
)
pause
