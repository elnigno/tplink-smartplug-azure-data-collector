# TP-Link HS110 Data Collector for Azure

Simple python script to collect energy consumption data from a TP-Link HS110 smart plug and send it to an Azure IoT hub.

It is basically a combination of [a tutorial to send telemetry to Azure](https://docs.microsoft.com/en-us/azure/iot-hub/quickstart-send-telemetry-python) and [this other script](https://www.beardmonkey.eu/tplink/hs110/2017/11/21/collect-and-store-realtime-data-from-the-tp-link-hs110.html) that does something very similar (but stores data to Graphite instead). This last script is in turn based on [this reverse engineering work](https://github.com/softScheck/tplink-smartplug).


## Usage

Change the values of the IoT Hub `CONNECTION_STRING` (see how to get it [here](https://docs.microsoft.com/en-us/azure/iot-hub/quickstart-send-telemetry-python)) and `DEVICE_IP`, then just run `python collect.py`.

## Dependencies

`pip install azure-iothub-device-client`
