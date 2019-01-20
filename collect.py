import sys
import time
import socket
import json
import threading
from struct import pack

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "ConnectionString"
DEVICE_IP = "XXX.XXX.XXX.XXX"

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

# Define the JSON message to send to IoT Hub.
MSG_TXT = "{\"time\": %d,\"current\": %d, \"voltage\": %d, \"power\": %d}"

def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += chr(a)
    return result

def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ ord(i)
        key = ord(i)
        result += chr(a)
    return result
    
def send_hs_command(address, port, cmd):
    data = b""

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_sock.connect((address, port))
        tcp_sock.send(encrypt(cmd))
        data = tcp_sock.recv(2048)
    except socket.error:
        print("Socket closed.")
    finally:
        tcp_sock.close()
    return data

def send_to_cloud(current, voltage, power):
    current_time = time.time()

    try:
        msg_txt_formatted = MSG_TXT % (current_time, current, voltage, power)
        message = IoTHubMessage(msg_txt_formatted)

        # Send the message.
        print( "Sending message: %s" % message.get_string() )
        client.send_event_async(message, send_confirmation_callback, None)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

def data_to_map(data):
    decrypted_data = decrypt(data[4:]).decode()
    json_data = json.loads(decrypted_data)
    return json_data["emeter"]["get_realtime"]
    
def run():
    threading.Timer(60.0, run).start()

    data = send_hs_command(DEVICE_IP, 9999, b'{"emeter":{"get_realtime":{}}}')

    if not data:
        print("No data returned on power request.")
        store_metrics(0, 0, 0)
        return

    emeter = data_to_map(data)

    if not emeter:
        print("No emeter data returned on power request.")
        store_metrics(0, 0, 0)
        return

    send_to_cloud(emeter["current_ma"], emeter["voltage_mv"], emeter["power_mw"])

client = iothub_client_init()
run()
