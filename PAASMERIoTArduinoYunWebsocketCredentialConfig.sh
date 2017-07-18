#!/usr/bin/expect
# This script helps to upload the targeted file/directory to remote Arduino Yun Board

# Args check
if {$argc!=5} {
	send_user "usage: ./PAASMERIoTArduinoYunWebsocketCredentialConfig.sh <Board IP> <UserName> <Board Password> <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY>\n"
	exit
}

set timeout 10
set ArduinoYunIPAddress [lindex $argv 0]
set ArduinoYunUserName [lindex $argv 1]
set ArduinoYunPassword [lindex $argv 2]
set AWS_ACCESS_KEY_ID [lindex $argv 3]
set AWS_SECRET_ACCESS_KEY [lindex $argv 4]
set RemoteEndpoint "$ArduinoYunUserName@$ArduinoYunIPAddress"
set profileFullPath "/etc/profile"

send_user "Arduino Yun IP is: $ArduinoYunIPAddress\n"
send_user "Arduino Yun User Name is: $ArduinoYunUserName\n"
send_user "New environment variables will be added to Arduino Yun:\n"
send_user "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID\n"
send_user "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY\n"
send_user "$profileFullPath will be modified.\n"
send_user "Please wati until the program exits.\n\n"

# ssh into Arduino Yun and modify $profileFullPath
spawn ssh $RemoteEndpoint
expect {
    # In case this is the first time
    -re ".*yes/no.*" {
        send "yes\r"; exp_continue
	-re ".*assword.*" { send  "$ArduinoYunPassword\r" }
    }
    -re ".*assword.*" { send "$ArduinoYunPassword\r" }
}
# Insert new environment variables
expect "*~#" {
	# In case we need to update credentials
	# Remove the existing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
	send "sed -i '/^export AWS_ACCESS_KEY_ID=/'d /etc/profile\r"
	send "sed -i '/^export AWS_SECRET_ACCESS_KEY=/'d /etc/profile\r"
	# Append the new credentials to the end of the file
	send "echo export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID >> /etc/profile\r"
	send "echo export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY >> /etc/profile\r"
	# Enable the new profile
	send "source /etc/profile\r"
}
expect "*~#" { send "exit\r" }
# Notification to the user to power-cycle the board
send_user "Credentials added to Yun as environment variables. Now please power-cycle the board."
send_user "Exiting..."
# End of the configuration
interact



