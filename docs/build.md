# make.bat
執行 [make.bat] 將程式打包成執行檔。

### 取得當前目錄
```bash
cd %~dp0
```

### 使用 [pyinstaller] 編譯成執行檔
```bash
pyinstaller -y server_run.spec
```

### 使用 [xcopy] 指令，複製執行檔所需的資料
```bash
set SOURCE_DIR=%~dp0
set DEST_DIR=%~dp0\dist\item_manager
xcopy "%SOURCE_DIR%\templates\" "%DEST_DIR%\templates\" /s /e /i /y
xcopy "%SOURCE_DIR%\static\" 	"%DEST_DIR%\static\" 	/s /e /i /y
xcopy "%SOURCE_DIR%\writable\" 	"%DEST_DIR%\writable\" 	/s /e /i /y
```

### 使用 Compress-Archive 指令，將打包好的資料夾壓縮
```bash
set FOLDER_TO_COMPRESS=%DEST_DIR%\*
set OUTPUT_FILE=%DEST_DIR%.zip
powershell -command "Compress-Archive -Path '%FOLDER_TO_COMPRESS%' -Force -DestinationPath '%OUTPUT_FILE%'"
```

### 顯示完成
```bash
echo completed.

pause
```

[make.bat]: ../make.bat
[pyinstaller]: https://pypi.org/project/pyinstaller/
[xcopy]: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/xcopy
[compress-archive]: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/compress-archive?view=powershell-7.4