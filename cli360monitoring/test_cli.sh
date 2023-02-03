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

    # check if result contains "ERROR:" and exit if it does
    LINE=$(grep -m 1 "ERROR:" "$LOG_FILE")
    if [[ -n "$LINE" ]]; then
        echo
        echo "-------------------------------------"
        echo " Test failed for $1"
        echo "-------------------------------------"
        exit 1
    fi
}

if [[ -n $1 ]]; then
    CMD="$1"
else
    CMD="./cli360monitoring.py"
fi

echo "--- Test $NOW ---" > "$LOG_FILE"

test "$CMD"
test "$CMD config --print"
test "$CMD statistics"
test "$CMD usertokens --list"
test "$CMD contacts --list"
test "$CMD sites --list"
test "$CMD sites --list --csv"
test "$CMD servers --list"
test "$CMD servers --add"
test "$CMD servers --remove"

test "$CMD sites --add www.bild.de"
sleep 10
test "$CMD sites --get www.bild.de"
test "$CMD sites --remove www.bild.de"

echo
echo "-------------------------------------"
echo " Test successfull"
echo "-------------------------------------"
