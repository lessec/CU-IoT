import asyncio
import geocoder
import os
import logging

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import MethodResponse
import helper

logging.basicConfig(level=logging.ERROR)

# ID value to connect with IoT Central
location_info_digital_model_identifier = "dtmi:azure:LocationManagement:LocationInformation;1"
driver_info_digital_model_identifier = "dtmi:azure:DriverManagement:DriverInformation;1"
model_id = "dtmi:heetakyangIot:HeartRateChecker6cr;1"

location_information_component_name = "locationInformation"
driver_information_component_name = "driverInformation"


# Actions to reboot sample of command, not use this simulation but use test
async def reboot_handler(values):
    if values:
        print("Rebooting after {delay} seconds".format(delay=values))
    print("Rebooting finished")


async def heartRate_simulation_value(device_client, telemetry_msg, component_name=None):
    msg = helper.create_telemetry(telemetry_msg, component_name)
    await device_client.send_message(msg)
    print("\n")
    print(msg)
    await asyncio.sleep(1)


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
        print("\n--> Successfully reported an emergency\n")
        selection = input("--> If want continue, enter any key\n")
        if selection != None:
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
    # Get location through my current ip
    coordinates = geocoder.ip("me")
    geo_index = coordinates.latlng
    geo_lat = geo_index[0]
    geo_lng = geo_index[1]
    geo_alt = None  # Replaced the altitude with Null Cause' find location by IP.

    geo_street = coordinates.street
    geo_city = coordinates.city
    geo_state = coordinates.state
    geo_country = coordinates.country
    # geojosn = OrderedDict()   # Generate json code: test code
    # geojosn["carLocation"] = {"lat": geo_lat, "lon": geo_lng, "alt": geo_alt}

    # Organise location information value
    geojson = {"lat": geo_lat, "lon": geo_lng, "alt": geo_alt}
    properties_location_info = helper.create_reported_properties(
        location_information_component_name,
        carLocation=geojson,
        latValue=geo_lat,
        lngValue=geo_lng,
        altValue=geo_alt,
        streetValue=geo_street,
        cityValue=geo_city,
        stateValue=geo_state,
        countryValue=geo_country,
    )

    # Organise Driver information value
    properties_driver_info = helper.create_reported_properties(
        driver_information_component_name,
        vrn="GB BD51SMR",
        vehicleName="Jaguar XF",
        vehicleManufacturer="Jaguar Cars",
        driverName="Jane Doe",
        bloodyType="A+",
        currentStatus="Low heart rate, dizzy",
        currentSituation="Dangerous",
    )

    # Send location and driver information to Device of IoT Central
    property_updates = asyncio.gather(
        device_client.patch_twin_reported_properties(properties_location_info),
        device_client.patch_twin_reported_properties(properties_driver_info),
    )

    print("\nListening for command requests and property updates")

    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished

    if not property_updates.done():
        property_updates.set_result("DONE")

    property_updates.cancel()

    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
