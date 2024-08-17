@echo off
conda activate pico

set sid=%1
set loc=%2
set notes=%3

powershell -File .\flash_station.ps1