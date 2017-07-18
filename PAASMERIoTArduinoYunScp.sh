#!/usr/bin/expect
# This script helps to upload the targeted file/directory to remote Arduino Yun Board

# Args check
if {$argc!= 5} {
    send_user "usage: ./PAASMERIoTArduinoYunScp.sh <Board IP> <UserName> <Board Password> <File> <Destination>\n"
    exit
}

set timeout 10
set ArduinoYunIPAddress [lindex $argv 0]
set ArduinoYunUserName [lindex $argv 1]
set ArduinoYunPassword [lindex $argv 2]
set TargetFile [lindex $argv 3]
set Destination [lindex $argv 4]
set RemoteEndpoint "$ArduinoYunUserName@$ArduinoYunIPAddress:$Destination"

send_user "Arduino Yun IP is: $ArduinoYunIPAddress\n"
send_user "Arduino Yun User Name is: $ArduinoYunUserName\n"
send_user "\nNow start transmitting $TargetFile to remote directory: $RemoteEndpoint ...\n"

# scp automatically creates the missing directory
spawn scp -r $TargetFile $RemoteEndpoint
expect {
    # In case this is the first time
    -re ".*yes/no.*" {
        send "yes\r"; exp_continue
	-re ".*assword.*" { send  "$ArduinoYunPassword\r" }
    }
    -re ".*assword.*" { send "$ArduinoYunPassword\r" }
}
expect {
    eof {
	send_user "Completed!\n"
    }
}