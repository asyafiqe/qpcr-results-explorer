setlocal enabledelayedexpansion
rem @echo off

set "url=https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
set "python_embed_zip=python_embeded.zip"

echo Downloading python embeded...

curl -o %python_embed_zip% %url%

if %errorlevel% neq 0 (
    echo Error: Failed to download python embeded.
    exit /b 1
)

echo Python embeded downloaded successfully.

set output_folder=release
set python_folder=%output_folder%\python_embeded

rem Create the destination folder if it doesn't exist
mkdir %python_folder% 2>nul

rem Use PowerShell to extract the zip file
powershell -Command "Expand-Archive -Force -Path '%python_embed_zip%' -DestinationPath '%python_folder%'"

del %python_embed_zip%

curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py

rem enable pip, uncomment import site
set "search=#import site"
set "replace=import site"
set "input_file=%python_folder%\python310._pth"
set "temp_file=temp_file._pth"

(for /f "delims=" %%a in ('type "%input_file%"') do (
    set "line=%%a"
    set "line=!line:%search%=%replace%!"
    echo !line!
)) > "%temp_file%"

move /y "%temp_file%" "%input_file%"

rem install pip
%python_folder%\python.exe get-pip.py
del get-pip.py

rem install requirement
%python_folder%\python.exe -m pip install -r requirements.txt

copy /y app.py %output_folder%\app.py
copy /y run.bat %output_folder%\run.bat
copy /y plate_id_example.csv %output_folder%\plate_id_example.csv

set folderToZip=%output_folder%
set zipFile=release.zip

powershell Compress-Archive -Path "%folderToZip%" -DestinationPath "%zipFile%"
rem rmdir /s /q "%folderToZip%"

endlocal

pause