'''
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
 '''

import os
import sys
sys.path.insert(0, "../lib/")
import AWSIoTPythonSDK
sys.path.insert(0, os.path.abspath(AWSIoTPythonSDK.__file__))
import logging
from threading import Lock
from util.jsonManager import jsonManager
from exception.AWSIoTExceptions import *
from comm.serialCommunicationServer import *
from command.AWSIoTCommand import *
from command.commandConnect import *
from command.commandDisconnect import *
from command.commandConfig import *
from command.commandPublish import *
from command.commandSubscribe import *
from command.commandUnsubscribe import *
from command.commandShadowGet import *
from command.commandShadowDelete import *
from command.commandShadowUpdate import *
from command.commandShadowRegisterDeltaCallback import *
from command.commandShadowUnregisterDeltaCallback import *
from command.commandYield import *
from command.commandLockSize import *
from command.commandJSONKeyVal import *
from command.commandSetBackoffTiming import *
from command.commandSetOfflinePublishQueueing import *
from command.commandSetDrainingIntervalSecond import *
# Use IoT Python SDK as backend
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from AWSIoTPythonSDK.MQTTLib import MQTTv3_1, MQTTv3_1_1
# import traceback


# Object for each MQTT subscription to hold the sketch info (slot #)
class _mqttSubscribeUnit:

    def __init__(self, srcFormatPayloadForYieldFunctionPointer):
        self._topicName = None
        self._sketchSlotNumber = -1
        self._formatPayloadForYield = None
        self._serialCommunicationServerHub = None
        self._formatPayloadForYield = srcFormatPayloadForYieldFunctionPointer

    def setTopicName(self, srcTopicName):
        self._topicName = srcTopicName

    def setSketchSlotNumber(self, srcSketchSlotNumber):
        self._sketchSlotNumber = srcSketchSlotNumber

    def setSerialCommunicationServerHub(self, srcSerialCommunicationServerHub):
        self._serialCommunicationServerHub = srcSerialCommunicationServerHub

    def getTopicName(self):
        return self._topicName

    def getSketchSlotNumber(self):
        return self._sketchSlotNumber

    def individualCallback(self, client, userdata, message):
        # Process the incoming non-shadow messages for a specific MQTT subscription
        # Parse them into protocol-style chunks that can be transmitted over the serial
        # and understood by Atmega
        # Execution of this callback is ATOMIC (Guaranteed by paho)
        ####
        # Get the topic
        currentTopic = str(message.topic)
        # Find the sketch slot related to this topic name, ignore if not exist any more
        try:
            currentSketchSlotNumber = self._sketchSlotNumber
            # Refactor the payload by adding protocol head and dividing into reasonable chunks
            formattedPayload = self._formatPayloadForYield(str(message.payload), currentSketchSlotNumber)
            # Put it into the internal queue of serialCommunicationServer
            self._serialCommunicationServerHub.writeToInternalYield(formattedPayload)
            # This message will get to be transmitted in future Yield requests
        except KeyError:
            pass  # Ignore messages coming between callback and unsubscription


class runtimeHub:
    
    #### Methods start here ####
    def __init__(self, srcFileName, srcLogDirectory):
        # Init with basic interface for serial communication
        self._log = logging.getLogger(__name__)
        self._serialCommunicationServerHub = serialCommunicationServer()
        self._serialCommunicationServerHub.setAcceptTimeout(10)
        self._serialCommunicationServerHub.setChunkSize(50)
        self._jsonManagerHub = jsonManager(512*3)  # Default history limits is set to be 512*3, 512 for accepted, 512 for rejected and 512 for deltas
        # Keep the record of MQTT subscribe sketch info (slot #), in forms of individual object
        self._mqttSubscribeTable = dict()
        # Keep the record of shadow subscribe sketch info (slot #)
        self._shadowSubscribeRecord = dict()
        # Keep track of the deviceShadow instances for each individual deviceShadow name
        self._shadowRegistrationTable = dict()
        # MQTT Connection
        self._mqttClientHub = None  # Init when requested
        self._shadowClientHub = None  # Init when requested
        # ShadowCallback Lock
        self._shadowCallbackLock = Lock()

    def _getAWSIoTMQTTShadowClient(self, clientID, protocol, useWebsocket, cleanSession):
        return AWSIoTMQTTShadowClient(clientID, protocol, useWebsocket, cleanSession)

    def _findCommand(self, srcProtocolMessage):
        # Whatever comes out of this method should be an AWSIoTCommand
        # Invalid command will have a protocol name of "x"
        # Never raise exceptions
        retCommand = None
        if srcProtocolMessage is None:
            retCommand = AWSIoTCommand.AWSIoTCommand()
        else:
            # MQTT init
            if srcProtocolMessage[0] == "i":
                retCommand = AWSIoTCommand.AWSIoTCommand("i")
                if len(srcProtocolMessage[1:]) == 4:
                    clientID = srcProtocolMessage[1]
                    cleanSession = srcProtocolMessage[2] == "1"
                    protocol = MQTTv3_1
                    if srcProtocolMessage[3] == "4":
                        protocol = MQTTv3_1_1
                    useWebsocket = srcProtocolMessage[4] == "1"
                    try:
                        self._shadowClientHub = self._getAWSIoTMQTTShadowClient(clientID, protocol, useWebsocket, cleanSession)
                        self._shadowClientHub.configureConnectDisconnectTimeout(10)
                        self._shadowClientHub.configureMQTTOperationTimeout(5)
                        self._mqttClientHub = self._shadowClientHub.getMQTTConnection()
                    except TypeError:
                        retCommand.setInitSuccess(False)  # Error in Init, set flag 
                else:
                    retCommand.setInitSuccess(False)  # Error in obtain parameters for Init
            # Config
            elif srcProtocolMessage[0] == "g":
                retCommand = commandConfig(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowClientHub)
            # Connect
            elif srcProtocolMessage[0] == "c":
                retCommand = commandConnect(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowClientHub)
            # Disconnect
            elif srcProtocolMessage[0] == "d":
                retCommand = commandDisconnect(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowClientHub)
            # Publish
            elif srcProtocolMessage[0] == "p":
                retCommand = commandPublish(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub)
            # Subscribe
            elif srcProtocolMessage[0] == "s":
                newMQTTSubscribeUnit = _mqttSubscribeUnit(self._formatPayloadForYield)  # Init an individual object for this subscribe
                newSrcProtocolMessage = srcProtocolMessage
                newSrcProtocolMessage.append(newMQTTSubscribeUnit)
                retCommand = commandSubscribe(newSrcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub, self._mqttSubscribeTable)
            # Unsubscribe
            elif srcProtocolMessage[0] == "u":
                retCommand = commandUnsubscribe(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub, self._mqttSubscribeTable)
            # Shadow init
            elif srcProtocolMessage[0] == "si":
                retCommand = AWSIoTCommand.AWSIoTCommand("si")
                if self._shadowClientHub is None:
                    # Should have init a mqttCore and got it connected
                    retCommand.setInitSuccess(False)
                else:
                    # Now register the requested deviceShadow name
                    if len(srcProtocolMessage[1:]) == 2:
                        srcShadowName = srcProtocolMessage[1]
                        srcIsPersistentSubscribe = srcProtocolMessage[2] == "1"
                        try:
                            newDeviceShadow = self._shadowClientHub.createShadowHandlerWithName(srcShadowName, srcIsPersistentSubscribe)
                            # Now update the registration table
                            self._shadowRegistrationTable[srcShadowName] = newDeviceShadow
                        except TypeError:
                            retCommand.setInitSuccess(False)
                    else:
                        retCommand.setInitSuccess(False)
            # Shadow get
            elif srcProtocolMessage[0] == "sg":
                newSrcProtocolMessage = srcProtocolMessage
                newSrcProtocolMessage.append(self._shadowCallback)
                retCommand = commandShadowGet(newSrcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowRegistrationTable, self._shadowSubscribeRecord)
            # Shadow update
            elif srcProtocolMessage[0] == "su":
                newSrcProtocolMessage = srcProtocolMessage
                newSrcProtocolMessage.append(self._shadowCallback)
                retCommand = commandShadowUpdate(newSrcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowRegistrationTable, self._shadowSubscribeRecord)
            # Shadow delete
            elif srcProtocolMessage[0] == "sd":
                newSrcProtocolMessage = srcProtocolMessage
                newSrcProtocolMessage.append(self._shadowCallback)
                retCommand = commandShadowDelete(newSrcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowRegistrationTable, self._shadowSubscribeRecord)
            # Shadow register delta
            elif srcProtocolMessage[0] == "s_rd":
                newSrcProtocolMessage = srcProtocolMessage
                newSrcProtocolMessage.append(self._shadowCallback)
                retCommand = commandShadowRegisterDeltaCallback(newSrcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowRegistrationTable, self._shadowSubscribeRecord)
            # Shadow unregister delta
            elif srcProtocolMessage[0] == "s_ud":
                retCommand = commandShadowUnregisterDeltaCallback(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._shadowRegistrationTable, self._shadowSubscribeRecord)
            # Lock message size
            elif srcProtocolMessage[0] == "z":
                retCommand = commandLockSize(srcProtocolMessage[1:], self._serialCommunicationServerHub)
            # Oh the GREAT yield...
            elif srcProtocolMessage[0] == "y":
                retCommand = commandYield(srcProtocolMessage[1:], self._serialCommunicationServerHub)
            # JSON Key-Value Retrieve
            elif srcProtocolMessage[0] == 'j':
                retCommand = commandJSONKeyVal(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._jsonManagerHub)
            # Backoff Timing Config
            elif srcProtocolMessage[0] == 'bf':
                retCommand = commandSetBackoffTiming(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub)
            # Offline Publish Queue Config
            elif srcProtocolMessage[0] == 'pq':
                retCommand = commandSetOfflinePublishQueueing(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub)
            # Draining Interval Config
            elif srcProtocolMessage[0] == 'di':
                retCommand = commandSetDrainingIntervalSecond(srcProtocolMessage[1:], self._serialCommunicationServerHub, self._mqttClientHub)
            # Exit the runtimeHub
            elif srcProtocolMessage[0] == "~":
                retCommand = AWSIoTCommand.AWSIoTCommand("~")
            # Unsupported protocol
            else:
                retCommand = AWSIoTCommand.AWSIoTCommand()
        return retCommand

    def _formatPayloadForYield(self, srcPayload, srcSketchSlotNumber):
        # Generate the formatted payload for Yield requests
        ####
        # Generate the meta data
        hasMore = 1
        metaData = "Y " + str(srcSketchSlotNumber) + " " + str(hasMore) + " "
        # Get configured chunk size
        configuredChunkSize = self._serialCommunicationServerHub.getChunkSize()
        # Divide the payload into smaller chunks plus  meta data
        messageChunkSize = configuredChunkSize - len(metaData)
        chunks = [metaData + srcPayload[i:i+messageChunkSize] for i in range(0, len(srcPayload), messageChunkSize)]
        # Change hasMore flag for the last chunk
        chunks[len(chunks)-1] = "Y " + str(srcSketchSlotNumber) + " 0 " + chunks[len(chunks)-1][len(metaData):]
        # Concat them together
        return "".join(chunks)        

    # Callbacks
    def _shadowCallback(self, srcPayload, srcCurrentType, srcCurrentToken):
        # Process the incoming shadow messages
        # Store JSON payload into jsonManager and pass the handler over
        # Parse the handler into protocol-style chunks that can be transimitted over the serial
        # and understood by Atmega
        # Execution of this callback can be in separate threads (SDK), therefore an extra lock is added here
        # All token/version controls are performed at deviceShadow level
        # Whatever comes in here should be delivered across serial, with care, of course
        ####
        # srcCurrentType: accepted//rejected//<deviceShadowName>/delta
        self._shadowCallbackLock.acquire()
        currentJSONHandler = self._jsonManagerHub.storeNewJSON(srcPayload, srcCurrentType)
        currentSketchSlotNumber = -1
        try:
            # Wait util internal data structure is updated
            if srcCurrentToken is not None:
                while srcCurrentToken not in self._shadowSubscribeRecord.keys():
                    pass
            # accepted//rejected: Find the sketch slot number by token
            if srcCurrentType in ["accepted", "rejected", "timeout"]:
                currentSketchSlotNumber = self._shadowSubscribeRecord[srcCurrentToken]
                del self._shadowSubscribeRecord[srcCurrentToken]  # Retrieve the memory in dict
            # delta/<deviceShadowName>: Find the sketch slot number by deviceShadowName
            else:
                fragments = srcCurrentType.split("/")
                deviceShadowNameForDelta = fragments[1]
                currentSketchSlotNumber = self._shadowSubscribeRecord[deviceShadowNameForDelta]
            # Refactor the JSONHandler by adding protocol head and dividing into reasonable chunks
            formattedPayload = self._formatPayloadForYield(currentJSONHandler, currentSketchSlotNumber)
            # Put it into the internal queue of the serialCommunicationServer
            self._serialCommunicationServerHub.writeToInternalYield(formattedPayload)
            # This message will get to be transmitted in future Yield requests
        except KeyError as e:
            self._shadowCallbackLock.release()
            return
            # Ignore messages coming between callback and unregister delta 
        self._shadowCallbackLock.release()

    # Runtime function
    def run(self):
        while True:
            try:
                # Start the serialCommunicationServer and accepts protocol messages
                # Raises AWSIoTExceptions.acceptTimeoutException
                currentProtocolMessage = self._serialCommunicationServerHub.accept()
                # Find with command request this is
                currentCommand = self._findCommand(currentProtocolMessage)
                # See if the command is an init (MQTT/Shadow) that needs data structure operations
                currentCommandProtocolName = currentCommand.getCommandProtocolName()
                if currentCommandProtocolName == "x":
                    pass # Ignore invalid protocol command
                if currentCommandProtocolName == "i":  # MQTT init
                    if currentCommand.getInitSuccess():
                        self._serialCommunicationServerHub.writeToInternalProtocol("I T")
                    else:
                        self._serialCommunicationServerHub.writeToInternalProtocol("I F")
                    self._serialCommunicationServerHub.writeToExternalProtocol()
                elif currentCommandProtocolName == "si":  # Shadow init
                    if currentCommand.getInitSuccess():
                        self._serialCommunicationServerHub.writeToInternalProtocol("SI T")
                    else:
                        self._serialCommunicationServerHub.writeToInternalProtocol("SI F")
                    self._serialCommunicationServerHub.writeToExternalProtocol()
                elif currentCommandProtocolName == "~":  # Exit
                    break
                else:  # Other command
                    # Execute the command
                    currentCommand.execute()
                    # Write the result back through serial (detailed error code is transmitted here)
                    if currentCommandProtocolName == "y":
                        self._serialCommunicationServerHub.writeToExternalYield()
                    elif currentCommandProtocolName == "j":
                        self._serialCommunicationServerHub.writeToExternalJSON()
                    else:
                        self._serialCommunicationServerHub.writeToExternalProtocol()

            except AWSIoTExceptions.acceptTimeoutException as e:
                self._log.debug(str(e.message))
                break
            except Exception as e:
                self._log.debug("Exception in run: " + str(type(e)) + str(e.message))
                # traceback.print_exc(file, sys.stdout)
