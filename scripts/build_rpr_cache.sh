#!/bin/bash
export PYTHONPATH=$PWD/../jobs/Scripts:$PYTHONPATH
export MAYA_SCRIPT_PATH=$PWD/../jobs/Scripts:$MAYA_SCRIPT_PATH
export MAYA_CMD_FILE_OUTPUT=$PWD/../templog

TOOL=${1:-2022}
export ENGINE=${2:-Northstar}

maya${TOOL} -command "python(\"import cache_building\")" -file "$CIS_TOOLS/../TestResources/usd_maya_autotests/Scenes/Kitchen.ma"

echo "--------Script editor log--------"
cat $MAYA_CMD_FILE_OUTPUT
