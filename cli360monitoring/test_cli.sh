#!/bin/bash
#
################################################################################
##          Test 360 Monitoring CLI                                           ##
################################################################################

LOG_FILE="test.log"
NOW=$(date +'%Y-%m-%d %a %T')

# Function to test a CLI call
# Parameters: 1 command
function test
{
    echo "$1"
    echo "$1" >> "$LOG_FILE"
    $1 >> "$LOG_FILE"

    # check if result contains "Traceback" and exit if it does
    LINE=$(grep -m 1 "Traceback" "$LOG_FILE")
    if [[ -n "$LINE" ]]; then
        echo
        echo "-------------------------------------"
        echo " Test failed for $1"
        echo "-------------------------------------"
        exit 1
    fi
}

echo "--- Test $NOW ---" > "$LOG_FILE"

test "./cli360monitoring.py"
test "./cli360monitoring.py config --print"
test "./cli360monitoring.py statistics"
test "./cli360monitoring.py usertokens --list"
test "./cli360monitoring.py contacts --list"
test "./cli360monitoring.py sites --list"
test "./cli360monitoring.py sites --list --csv"
test "./cli360monitoring.py servers --list"
test "./cli360monitoring.py servers --add"
test "./cli360monitoring.py servers --remove"

test "./cli360monitoring.py sites --add www.bild.de"
sleep 10
test "./cli360monitoring.py sites --get www.bild.de"
test "./cli360monitoring.py sites --remove www.bild.de"

echo
echo "-------------------------------------"
echo " Test successfull"
echo "-------------------------------------"
