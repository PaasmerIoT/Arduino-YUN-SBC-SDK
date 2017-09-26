/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

#include <aws_iot_mqtt.h>
#include <aws_iot_version.h>
#include "aws_iot_config.h"
//#include "config.h"
#include<WiFi.h>
#include<string.h>

aws_iot_mqtt_client myClient; // init iot_mqtt_client
char msg[650]; // read-write buffer
int cnt = 1; // loop counts
int rc = -200; // return value placeholder
bool success_connect = false; // whether it is connected
int val = 0;     // variable to store the read value
int a;
byte mac_id[6];
char topicName[50];
String message;
// Basic callback function that prints out the message
void msg_callback(char* src, unsigned int len, Message_status_t flag) {
  if(flag == STATUS_NORMAL) {
    Serial.println("CALLBACK:");
    int i;
       Serial.print(src);
     Serial.println("");
    for(i=0;feedpin[i];i++)
    {
      if(strstr(src,feedname[i])){
      if(!strcmp(feedtype[i],"actuator")){
        if(strstr(src,"on")){
          digitalWrite(feedpin[i],HIGH);
          }
          else{
            digitalWrite(feedpin[i],LOW);
            }
          }
      }
      
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.print("started");
  
  while(!Serial);
     for(a=0;feedpin[a];a++){
    if(!strcmp(feedtype[a],"sensor")){
      pinMode(feedpin[a], INPUT);}
    else {
      pinMode(feedpin[a],OUTPUT);
      }
    }
    

 char curr_version[50];
  snprintf_P(curr_version, 50, PSTR("Paasmer IoT SDK Version(dev) %d.%d.%d-%s\n"), VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_TAG);
  Serial.println(curr_version);
  
  strcpy(topicName,UserName);
  strcat(topicName,"_");
  strcat(topicName,DeviceName);
  Serial.println(topicName);
  // Set up the client
  if((rc = myClient.setup(AWS_IOT_CLIENT_ID)) == 0) {
    // Load user configuration
    if((rc = myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH)) == 0) {
      // Use default connect: 60 sec for keepalive
      if((rc = myClient.connect()) == 0) {
        success_connect = true;
        // Subscribe to "topic1"
      if((rc = myClient.subscribe(topicName, 1, msg_callback)) != 0) {
          Serial.println(F("Subscribe failed!"));
          Serial.println(rc);
        }
      }
      else {
        Serial.println(F("Connect failed!"));
        Serial.println(rc);
      }
    }
    else {
      Serial.println(F("Config failed!"));
      Serial.println(rc);
    }
  }
  else {
    Serial.println(F("Setup failed!"));
    Serial.println(rc);
  }
  // Delay to make sure SUBACK is received, delay time could vary according to the server
  delay(3000);
}

void loop() {
  int i;
  
  if(success_connect) {
    
		// Generate a new message in each loop and publish to "topic1"
   for (i=0;feedpin[i];i++){
        snprintf(msg,sizeof(msg),"{\"feeds\":[{\"feedname\":\"%s\",\"feedtype\":\"%s\",\"feedpin\":\"%d\",\"feedvalue\":\"%d\"}],\"messagecount\":\"%d\",\"paasmerid\":\"%x\",\"username\":\"%s\",\"devicename\":\"%s\",\"devicetype\":\"YUN\",\"ThingName\":\"%s\"}",feedname[i],feedtype[i],feedpin[i],digitalRead(feedpin[i]),cnt,mac_id[3],UserName,DeviceName,ThingName);
  if((rc = myClient.publish("paasmerv2_device_online_develop", msg, strlen(msg), 1, false)) != 0) {
      Serial.println(F("Publish failed!"));
      Serial.println(rc);
    }
   
    // Get a chance to run a callback
    if((rc = myClient.yield()) != 0) {
      Serial.println(F("Yield failed!"));
      Serial.println(rc);
    }
   
    // Done with the current loops
    sprintf_P(msg, PSTR("loop %d done"), cnt++);
    Serial.println(msg);
    delay(2000);
   }  
    delay(5000);
  }
}
