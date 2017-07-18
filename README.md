## Arduino-Yún-SDK

## What is PAASMER IoT Arduino Yún SDK

The PAASMER-IoT-Arduino-Yún-SDK allows developers to connect their Arduino Yún compatible Board to PAASMER IoT. By connecting the device to the PAASMER IoT, users can securely work with the message broker provided by PAASMER IoT.

* [Overview](#overview)
* [Installation](#installation)
* [Example](#example)
* [Support](#support)

<a name="overview"></a>
## Overview
This document provides step by step instructions to install the Arduino Yún SDK and connect your device to the PAASMER IoT.  
The PAASMER-IoT-Arduino-Yún-SDK which takes use of the resources of two chips on Arduino Yún for functionality and connections to the PAASMER IoT.

#### MQTT connection
The **PAASMER-IOT-ARDUINO-YUN-SDK** provides functionality to create and maintain a mutually authenticated TLS connection over which it runs **MQTT**. This connection is used for any further publish operations and allow for subscribing to **MQTT** topics which will call a configurable callback function when these topics are received.

#### Pre Requisites

Registration on the portal http://developers.paasmer.co, is necessary to connect the devices to the **Paasmer IoT Platfrom** .

<a name="installation"></a>
## Installation

* Download the SDK or clone it using the command below.
```
$ git clone https://github.com/PaasmerIoT/C-SDK-V2_0_1_2.git
$ cd C-SDK-V2_0_1_2
```

* To connect the device to Paasmer IoT Platfrom, the following steps need to be performed.

```
$ sudo ./install.sh
```

This will install all required softwares.
* To register the device to the Paasmer IoT Platform, the following command need to be executed.

```
$ sudo ./paasmerDeviceRegistration.sh
```
This will ask for the device name. Give a unique device name for your device and that must be alphanumeric[a-z A-Z 0-9].

* Upon successful completion of the above command, the following commands need to be executed.
```
echo "-->  1) sudo su "
echo "-->  2) source ~/.bashrc "
echo "-->  3) PAASMER_THING "
echo "-->  4) PAASMER_POLICY "
echo "-->  5) sed -i 's/alias PAASMER/#alias PAASMER/g' ~/.bashrc "
echo "-->  6) exit "
$ exit
```

### Set up your Arduino Yún Board
Please follow the instructions from official website: [Arduino Yún Guide](https://www.arduino.cc/en/Guide/ArduinoYun).

### Installation on Mac OS/Linux
Before proceeding to the following steps, please make sure that you have `expect` installed on your computer and correctly installed the Arduino IDE.  

For Arduino IDE installation on Linux, please visit [here](http://playground.arduino.cc/Linux/All).

1. Setup the Arduino Yún board and connect it to WiFi. Obtain its IP address and password.  
2. Make sure your computer is connected to the same network (local IP address range).  

3. Open a terminal,
* Then run the following script to update the changed into the Arduino Yun Board.

```
$ sudo ./PAASMERIoTArduinoYunInstallAll.sh <Board IP> <UserName> <Board Password>

```

This script will upload the python runtime code base and credentials to openWRT running on the more powerful micro-controller on you Arduino Yún board.  
This script will also download and install libraries for openWRT to implement the necessary scripting environment as well as communication protocols.

  It can take 10-15 minutes for the device to download and install the required packages.  

  NOTE: Do NOT close the terminal before the script finishes, otherwise you have to start over with this step. Make sure you are in your local terminal before repeating this step.  

4. Copy and paste `C-SDK-V2_0_1_2/PAASMER-IoT-Arduino-Yun-Library` folder into Arduino libraries that was installed with your Arduino SDK installation. For Mac OS default, it should be under `Documents/Arduino/libraries`.
5. Restart the Arduino IDE if it was running during the installation. You should be able to see the PAASMER IoT examples in the Examples folder in your IDE.  

There are the other two scripts: `PAASMERIoTArduinoYunScp.sh` and `PAASMERIoTArduinoYunSetupEnvironment.sh`, which are utilized in `PAASMERIoTArduinoYunInstallAll.sh`. You can always use `PAASMERIoTArduinoYunScp.sh` to upload your new credentials to your board. When you are in the directory `Arduino-Yun-SDK/`, the command should be something like this:  

    ./PAASMERIoTArduinoYunScp.sh <Board IP> <UserName> <Board Password> <File> <Destination>

<a name="example"></a>
## Example

### BasicPubSub
* See the PAASMER IoT examples in the Examples folder in your IDEdemonstrates a simple MQTT publish/subscribe using PAASMER IoT from Arduino Yún board. It first subscribes to a topic once and registers a callback to print out new messages to Serial monitor and then publishes to the topic in a loop. Whenever it receives a new message, it will be printed out to Serial monitor indicating the callback function has been called.

* Edit the config.h file to include the user name(Email), device name, feed names and GPIO pin details.

```c
#define UserName "Email Address" //your user name in website

#define timePeriod 6 //change the time delay as you required for sending actuator values to paasmer cloud

char* feedname[]={"feed1","feed2","feed3","feed4","feed5",.....}; //feed names you use in the website

char* feedtype[]={"actuator","sensor","sensor","actuator","actuator",.....}; //modify with the type of feeds i.e., actuator or sensor

int feedpin[]={3,5,7,11,13,....}; //modify with the pin numbers which you connected devices (actuator or sensor)
```

* **Hardware Required**  
Arduino Yún  
Computer connected with Arduino Yún using USB serial

* **Software Required**  
Arduino IDE

* **Circuit Required**  
Connect the sensors and actuators

* **Attention**  
Please make sure to start the example sketch after the board is fully set up and openWRT is up and connected to WiFi.

<a name="support"></a>
## Support
The support forum is hosted on the GitHub, issues can be identified by users and the Team from Paasmer would be taking up requstes and resolving them. You could also send a mail to support@paasmer.co with the issue details for quick resolution.
