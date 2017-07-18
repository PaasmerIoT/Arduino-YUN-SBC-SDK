#!/bin/bash
# If input args not correct, echo usage
if [ $# -ne 3 ]; then
    echo "usage: ./PAASMERIoTArduinoYunInstallAll.sh <Board IP> <UserName> <Board Password>"
else
# Welcoming prompt
    echo "This script will install all of the depencies and upload the codebase and credentials to the targeted Arduino Yun Board for the AWS IoT Arduino Yun SDK, which includes:"
    echo "- Install dependencies"
    echo "- Upload codebase"
    echo "- Upload credentials"
    echo "Please make sure you have included your credentials (private key, certificate and rootCA) in PAASMER-IoT-Python-Runtime/certs/"
# Load in params
    yunBoardIP=$1
    yunBoardUserName=$2
    yunBoardPassword=$3
    pyLibDir="./PAASMER-IoT-Python-Runtime"
    certsDir="$pyLibDir/certs"
# Check to see if AWS-IoT-Python-Runtime/certs/ is empty
    if [ "`ls -A $certsDir`" = "" ]; then
	echo -e "\nIt seems there are no credentials in $certsDir. Please generate your credentials and put them in that directory.\n"
	exit
    fi
# Change permission of functional scripts
    echo "Changing permissions for functional scripts..."
    chmod 755 PAASMERIoTArduinoYunScp.sh
    chmod 755 PAASMERIoTArduinoYunSetupEnvironment.sh
    echo "Done."
# Now start uploading codebase and credentials
    echo "Uploading codebase and credentials..."
    ./PAASMERIoTArduinoYunScp.sh $yunBoardIP $yunBoardUserName $yunBoardPassword $pyLibDir /root/
    echo "Done."
# Now start installing codebase on Arduino Yun Board
    echo "Installing dependencies on Arduino Yun..."
    ./PAASMERIoTArduinoYunSetupEnvironment.sh $yunBoardIP $yunBoardUserName $yunBoardPassword
    echo "Done."
# End of this script
    echo "Execution completed!"
fi
