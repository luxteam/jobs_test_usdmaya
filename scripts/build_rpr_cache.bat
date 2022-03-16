set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%
set MAYA_CMD_FILE_OUTPUT=%CD%\..\templog

set TOOL=%1
set ENGINE=%2

if not defined TOOL set TOOL=2022
if not defined ENGINE set ENGINE=Northstar

"C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" -command "python(\"import cache_building\")" -file "C:\\TestResources\\usd_maya_autotests\\Scenes\\Kitchen.ma"

type %MAYA_CMD_FILE_OUTPUT%