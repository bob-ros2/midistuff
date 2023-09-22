@echo off
REM Windows start script for midirec.py https://gitlab.com/bob-ros2/midistuff

set /p choice="Do you want to start a single track recording (0) or record multiple tracks (1)? Choose 0 or 1: "
if /i "%choice%" == "0" goto single
if /i "%choice%" == "1" goto multi
goto end

:single
python midirec.py
goto end

:multi
python midirec.py -a 30
goto end

:end
echo done
