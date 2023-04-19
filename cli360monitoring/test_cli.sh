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

    # check if result contains "Failed" and exit if it does
    LINE=$(grep -m 1 "Failed" "$LOG_FILE")
    if [[ -n "$LINE" ]]; then
        echo
        echo "-------------------------------------"
        echo " Test failed for $1"
        echo "-------------------------------------"
        exit 1
    fi
}

echo "--- Test $NOW ---" > "$LOG_FILE"

test "360monitoring"
test "360monitoring --version"
test "360monitoring config"
test "360monitoring config --help"
test "360monitoring config print"
test "360monitoring config save"
test "360monitoring contacts"
test "360monitoring contacts add --name TestContact --email no-reply@webpros.com"
test "360monitoring contacts list"
test "360monitoring contacts list --csv"
test "360monitoring recommendations"
test "360monitoring incidents list --page-id 628e185426cd9d5c1430602e"
test "360monitoring servers"
test "360monitoring servers add"
test "360monitoring servers list"
test "360monitoring servers list --csv"
test "360monitoring servers list --issues --csv"
# test "360monitoring servers update --tag test"
test "360monitoring servers remove"
test "360monitoring sites"
test "360monitoring sites add --url www.bild.de"
test "360monitoring sites list"
test "360monitoring sites list --csv"
test "360monitoring sites list --issues --csv"
test "360monitoring sites list --help"
test "360monitoring sites events --url www.bild.de"
test "360monitoring sites uptime --url www.bild.de"
test "360monitoring sites uptime --url www.bild.de --start \"2023-01-01\" --monthly"
test "360monitoring statistics"
test "360monitoring usertokens"
test "360monitoring usertokens list"
test "360monitoring usertokens list --csv"
test "360monitoring wptoolkit"

sleep 10

test "360monitoring sites list --url www.bild.de"
test "360monitoring sites remove --url www.bild.de"
test "360monitoring contacts remove --name TestContact"

echo
echo "-------------------------------------"
echo " Test successfull"
echo "-------------------------------------"
