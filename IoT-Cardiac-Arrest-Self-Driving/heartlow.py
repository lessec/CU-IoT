import asyncio
import logging
import os
import random

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from datetime import timedelta, datetime
import helper

logging.basicConfig(level=logging.ERROR)

# ID value to connect with IoT Central
heartRate_simulator_digital_model_identifier = "dtmi:com:example:heartmonitor;1"
device_info_digital_model_identifier = "dtmi:azure:DeviceManagement:DeviceInformation;1"
model_id = "dtmi:heetakyangIot:HeartRateChecker6cr;1"

heartRate_component_name = "heartmonitor"
device_information_component_name = "deviceInformation"

serial_number = "nomotopic"

HEARTRATE = None


# Actions to current heart rate data of command, not use this simulation but use test
class HeartRate(object):
    def __init__(self, name, moving_win=10):
        self.moving_window = moving_win
        self.records = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.index = 0
        self.cur = 0
        self.max = 0
        self.min = 0
        self.avg = 0
        self.name = name

    def record(self, current_hr):
        self.cur = current_hr
        self.records[self.index] = current_hr
        self.max = self.calculate_max(current_hr)
        self.min = self.calculate_min(current_hr)
        self.avg = self.calculate_average()
        self.index = (self.index + 1) % self.moving_window

    def calculate_max(self, current_hr):
        if not self.max:
            return current_hr
        elif current_hr > self.max:
            return self.max

    def calculate_min(self, current_hr):
        if not self.min:
            return current_hr
        elif current_hr < self.min:
            return self.min

    def calculate_average(self):
        return sum(self.records) / self.moving_window

    def create_report(self):
        response_dict = {}
        response_dict["maxHR"] = self.max
        response_dict["minHR"] = self.min
        response_dict["avgHR"] = self.avg
        response_dict["startTime"] = (
            (datetime.now() - timedelta(0, self.moving_window * 8)).astimezone().isoformat()
        )
        response_dict["endTime"] = datetime.now().astimezone().isoformat()
        return response_dict


# Actions to reboot sample of command, not use this simulation but use test
async def reboot_handler(values):
    if values:
        print("Rebooting after {delay} seconds".format(delay=values))
    print("Rebooting finished")


async def max_min_handler(values):
    if values:
        print(
            "Will return the max, min and average heart rate from the specified time {since} to the current time".format(
                since=values
            )
        )
    print("Done generating")


def create_max_min_report_response(heartRate_name):
    if "heartRate;1" in heartRate_name and HEARTRATE:
        response_dict = HEARTRATE.create_report()
    else:
        response_dict = {}
        response_dict["maxHR"] = 0
        response_dict["minHR"] = 0
        response_dict["avgHR"] = 0
        response_dict["startTime"] = datetime.now().astimezone().isoformat()
        response_dict["endTime"] = datetime.now().astimezone().isoformat()

    print(response_dict)
    return response_dict


async def heartRate_simulation_value(device_client, telemetry_msg, component_name=None):
    msg = helper.create_telemetry(telemetry_msg, component_name)
    await device_client.send_message(msg)
    print("\n")
    print(msg)
    await asyncio.sleep(2)


# Actions to sample of command, not use this simulation but use test
async def execute_command_listener(
        device_client,
        component_name=None,
        method_name=None,
        user_command_handler=None,
        create_user_response_handler=None,
):
    while True:
        if component_name and method_name:
            command_name = component_name + "*" + method_name
        elif method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)
        print("Command request received with payload")
        values = command_request.payload
        print(values)

        if user_command_handler:
            await user_command_handler(values)
        else:
            print("No handler provided to execute")

        (response_status, response_payload) = helper.create_response_payload_with_status(
            command_request, method_name, create_user_response=create_user_response_handler
        )

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))


# Actions to send properties
async def execute_property_listener(device_client):
    while True:
        patch = await device_client.receive_twin_desired_properties_patch()
        print(patch)
        properties_dict = helper.create_reported_properties_from_desired(patch)

        await device_client.patch_twin_reported_properties(properties_dict)


# Quit and finish processing
def stdin_listener():
    while True:
        selection = input("\n---Enter y(Yes) or N(No) to continue simulation---\n")
        if selection == "y" or selection == "Y" or selection == "yes" or selection == "Yes" or selection == "YES":
            print("\n--> Keep going")
        if selection == "n" or selection == "N" or selection == "no" or selection == "No" or selection == "NO":
            break


# Main routine start here
async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )  # Get the value stored in config

    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()


# Main part
async def main():
    switch = os.getenv("IOTHUB_DEVICE_SECURITY_TYPE")
    if switch == "DPS":
        provisioning_host = (
            os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            if os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            else "global.azure-devices-provisioning.net"
        )
        id_scope = os.getenv("IOTHUB_DEVICE_DPS_ID_SCOPE")
        registration_id = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_ID")
        symmetric_key = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_KEY")

        registration_result = await provision_device(
            provisioning_host, id_scope, registration_id, symmetric_key, model_id
        )  # Connect with IoT Central stored in config

        if registration_result.status == "assigned":
            print("Device was assigned")
            print(registration_result.registration_state.assigned_hub)
            print(registration_result.registration_state.device_id)
            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=symmetric_key,
                hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,
                product_info=model_id,
            )
        else:
            raise RuntimeError(
                "Could not provision device. Aborting Plug and Play device connection."
            )

    elif switch == "connectionString":
        conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
        print("Connecting using Connection String " + conn_str)
        device_client = IoTHubDeviceClient.create_from_connection_string(
            conn_str, product_info=model_id
        )
    else:
        raise RuntimeError(
            "At least one choice needs to be made for complete functioning of this sample."
        )

    await device_client.connect()

    # Value to be updated in Device in IoT Central
    # Organise serial number value
    properties_root = helper.create_reported_properties(serialNumber=serial_number)

    # Organise heart rate value
    properties_heartRate = helper.create_reported_properties(
        heartRate_component_name, maxHRLastReboot=10.00
    )

    # Organise device information value (sample data)
    properties_device_info = helper.create_reported_properties(
        device_information_component_name,
        swVersion="8.3",
        manufacturer="Apple Inc.",
        model="MU6D2KH/A",
        osName="iOS",
        processorArchitecture="S4 SiP",
        processorManufacturer="ARM",
        totalStorage=16,
        totalMemory=10.79,
    )

    # Send serial number, heart rate and device information to Device of IoT Central
    property_updates = asyncio.gather(
        device_client.patch_twin_reported_properties(properties_root),
        device_client.patch_twin_reported_properties(properties_heartRate),
        device_client.patch_twin_reported_properties(properties_device_info),
    )

    print("\nListening for command requests and property updates")

    global HEARTRATE
    HEARTRATE = HeartRate(heartRate_component_name, 10)

    listeners = asyncio.gather(
        execute_command_listener(
            device_client, method_name="reboot", user_command_handler=reboot_handler
        ),
        execute_command_listener(
            device_client,
            heartRate_component_name,
            method_name="maxminReport",
            user_command_handler=max_min_handler,
            create_user_response_handler=create_max_min_report_response,
        ),
        execute_property_listener(device_client),
    )

    # Generate heart rate values as random: low values (40-59)
    async def send_telemetry():
        print("\n-->Start to sending heart rate simulating value to IoT Central")
        while True:
            curr_hr_ext = random.randrange(40, 60)
            HEARTRATE.record(curr_hr_ext)
            hr_value_msg1 = {"heartRate": curr_hr_ext}
            await heartRate_simulation_value(
                device_client, hr_value_msg1, heartRate_component_name
            )  # Keep asking cause' heart rate is low.
            print("--> Your heart rate is low.Are you okay now? (y/N)")

    send_telemetry_task = asyncio.ensure_future(send_telemetry())

    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    if not property_updates.done():
        property_updates.set_result("DONE")

    listeners.cancel()
    property_updates.cancel()

    send_telemetry_task.cancel()

    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
