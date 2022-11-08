# Automatic first aid in case of cardiac arrest with autonomous driving vehicle

### Demo of cardiac arrest simulation while driving with Azure IoT Central with Python

This project was made with Python and Azure IoT Central.

## Requirements

1. Ubuntu 20.04 LTS Tested on Ubuntu 20.04.03.

```shell
sudo apt update && sudo apt upgrade -y
# if you need system upgrade
```

2. Python 3.8 or later Development is 3.10, Ubuntu 3.8 and 3.9 have been tested.

```shell
sudo apt install -y python3 python3-pip git
```

3. Get code through git from the GitHub

```shell
https://github.com/leelsey/CU-Project/tree/main/Internet%20of%20Things/IoT-Cardiac-Arrest-Self-Driving
```

## Simple setting method

1. Install Ubuntu 20.04 LTS. A virtual environment is recommended.
2. Please update if possible.
3. Install the dependency library.
4. Please download the file from GitHub.
5. Run main.py. That's all!

## IoT Central setting

It must be set in IoT Central. The demo address is https://heetakyang-iot.azureiotcentral.com/ and the template says "
Heart Rate Checker". If you need to create a new one, please do the following:

1. Root Component: Heart Rate Checker

```json
{
  "@id": "dtmi:heetakyangIot:HeartRateChecker6cr;1",
  "@type": "Interface",
  "contents": [
    {
      "@type": "Property",
      "displayName": {
        "en": "Serial Number"
      },
      "name": "serialNumber",
      "schema": "string",
      "writable": false
    },
    {
      "@type": "Command",
      "commandType": "synchronous",
      "description": {
        "en": "Reboots the device after waiting the number of seconds specified."
      },
      "displayName": {
        "en": "Reboot"
      },
      "name": "reboot",
      "request": {
        "@type": "CommandPayload",
        "description": {
          "en": "Number of seconds to wait before rebooting the device."
        },
        "displayName": {
          "en": "Delay"
        },
        "name": "delay",
        "schema": "integer"
      }
    },
    {
      "@type": "Component",
      "displayName": {
        "en": "heartmonitor"
      },
      "name": "heartmonitor",
      "schema": "dtmi:com:example:heartmonitor;1"
    },
    {
      "@type": "Component",
      "displayName": {
        "en": "DeviceInfo"
      },
      "name": "deviceInformation",
      "schema": "dtmi:azure:DeviceManagement:DeviceInformation;1"
    },
    {
      "@id": "dtmi:heetakyangIot:HeartRateChecker6cr:driverInformation;1",
      "@type": "Component",
      "displayName": {
        "en": "DriverInfo"
      },
      "name": "driverInformation",
      "schema": "dtmi:azure:DriverManagement:DriverInformation;1"
    },
    {
      "@id": "dtmi:heetakyangIot:HeartRateChecker6cr:locationInformation;1",
      "@type": "Component",
      "displayName": {
        "en": "LocationInfo"
      },
      "name": "locationInformation",
      "schema": "dtmi:azure:LocationManagement:LocationInformation;1"
    }
  ],
  "displayName": {
    "en": "Heart Rate Checker"
  },
  "@context": [
    "dtmi:iotcentral:context;2",
    "dtmi:dtdl:context;2"
  ]
}
```

2. Component 1: Heart Monitor

```json
{
  "@id": "dtmi:com:example:heartmonitor;1",
  "@type": "Interface",
  "contents": [
    {
      "@type": "Telemetry",
      "description": {
        "en": "Temperature in degrees Celsius."
      },
      "displayName": {
        "en": "HeartRate"
      },
      "name": "heartRate",
      "schema": "integer"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Returns the max temperature since last device reboot."
      },
      "displayName": {
        "en": "Max Heart Rate since Last Reboot."
      },
      "name": "maxHRLastReboot",
      "schema": "double",
      "writable": false
    },
    {
      "@type": "Command",
      "description": {
        "en": "This command returns the max, min and average temperature from the specified time to the current time."
      },
      "displayName": {
        "en": "Max/Min Report"
      },
      "name": "maxminReport",
      "request": {
        "@type": "CommandPayload",
        "description": {
          "en": "Period to return the max-min report."
        },
        "displayName": {
          "en": "Since"
        },
        "name": "since",
        "schema": "dateTime"
      },
      "response": {
        "@type": "CommandPayload",
        "displayName": {
          "en": "Temperature Report"
        },
        "name": "tempReport",
        "schema": {
          "@type": "Object",
          "fields": [
            {
              "displayName": {
                "en": "Max temperature"
              },
              "name": "maxTemp",
              "schema": "double"
            },
            {
              "displayName": {
                "en": "Min temperature"
              },
              "name": "minTemp",
              "schema": "double"
            },
            {
              "displayName": {
                "en": "Average Temperature"
              },
              "name": "avgTemp",
              "schema": "double"
            },
            {
              "displayName": {
                "en": "Start Time"
              },
              "name": "startTime",
              "schema": "dateTime"
            },
            {
              "displayName": {
                "en": "End Time"
              },
              "name": "endTime",
              "schema": "dateTime"
            }
          ]
        }
      }
    }
  ],
  "displayName": {
    "en": "Heart Monitor"
  },
  "@context": [
    "dtmi:iotcentral:context;2",
    "dtmi:dtdl:context;2"
  ]
}
```

3. Component 2: Device Information

```json
{
  "@id": "dtmi:azure:DeviceManagement:DeviceInformation;1",
  "@type": "Interface",
  "contents": [
    {
      "@type": "Property",
      "description": {
        "en": "Company name of the device manufacturer. This could be the same as the name of the original equipment manufacturer (OEM). Ex. Contoso."
      },
      "displayName": {
        "en": "Manufacturer"
      },
      "name": "manufacturer",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Device model name or ID. Ex. Surface Book 2."
      },
      "displayName": {
        "en": "Device model"
      },
      "name": "model",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Version of the software on your device. This could be the version of your firmware. Ex. 1.3.45"
      },
      "displayName": {
        "en": "Software version"
      },
      "name": "swVersion",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Name of the operating system on the device. Ex. Windows 10 IoT Core."
      },
      "displayName": {
        "en": "Operating system name"
      },
      "name": "osName",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Architecture of the processor on the device. Ex. x64 or ARM."
      },
      "displayName": {
        "en": "Processor architecture"
      },
      "name": "processorArchitecture",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Name of the manufacturer of the processor on the device. Ex. Intel."
      },
      "displayName": {
        "en": "Processor manufacturer"
      },
      "name": "processorManufacturer",
      "schema": "string"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Total available storage on the device in kilobytes. Ex. 2048000 kilobytes."
      },
      "displayName": {
        "en": "Total storage"
      },
      "name": "totalStorage",
      "schema": "double"
    },
    {
      "@type": "Property",
      "description": {
        "en": "Total available memory on the device in kilobytes. Ex. 256000 kilobytes."
      },
      "displayName": {
        "en": "Total memory"
      },
      "name": "totalMemory",
      "schema": "double"
    }
  ],
  "displayName": {
    "en": "Device Information"
  },
  "@context": [
    "dtmi:iotcentral:context;2",
    "dtmi:dtdl:context;2"
  ]
}
```

4. Component 3: Driver Information

```json
{
  "@id": "dtmi:azure:DriverManagement:DriverInformation;1",
  "@type": "Interface",
  "contents": [
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:vrn;1",
      "@type": "Property",
      "displayName": {
        "en": "Vehicle Registration Number"
      },
      "name": "vrn",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:vehicleName;1",
      "@type": "Property",
      "displayName": {
        "en": "Vehicle Name"
      },
      "name": "vehicleName",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:vehicleManufacturer;1",
      "@type": "Property",
      "displayName": {
        "en": "Vehicle Manufacturer"
      },
      "name": "vehicleManufacturer",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:driverName;1",
      "@type": "Property",
      "displayName": {
        "en": "DriverName"
      },
      "name": "driverName",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:bloodyType;1",
      "@type": "Property",
      "displayName": {
        "en": "Bloody Type"
      },
      "name": "bloodyType",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:currentStatus;1",
      "@type": "Property",
      "displayName": {
        "en": "Current Status"
      },
      "name": "currentStatus",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:DriverManagement:DriverInformation:currentSituation;1",
      "@type": "Property",
      "displayName": {
        "en": "Current Situation"
      },
      "name": "currentSituation",
      "schema": "string"
    }
  ],
  "displayName": {
    "en": "Driver Information"
  },
  "@context": [
    "dtmi:iotcentral:context;2",
    "dtmi:dtdl:context;2"
  ]
}
```

5. Component 4: Location Information

```json
{
  "@id": "dtmi:azure:LocationManagement:LocationInformation;1",
  "@type": "Interface",
  "contents": [
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:carLocation;1",
      "@type": [
        "Property",
        "Location"
      ],
      "displayName": {
        "en": "Car Location"
      },
      "name": "carLocation",
      "schema": "geopoint",
      "writable": false
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:latValue;1",
      "@type": "Property",
      "displayName": {
        "en": "Latitude"
      },
      "name": "latValue",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:lngValue;1",
      "@type": "Property",
      "displayName": {
        "en": "Longitude"
      },
      "name": "lngValue",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:altValue;1",
      "@type": "Property",
      "displayName": {
        "en": "Altitude"
      },
      "name": "altValue",
      "schema": "string",
      "writable": false
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:streetValue;1",
      "@type": "Property",
      "displayName": {
        "en": "Street"
      },
      "name": "streetValue",
      "schema": "string"
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:cityValue;1",
      "@type": "Property",
      "displayName": {
        "en": "City"
      },
      "name": "cityValue",
      "schema": "string"
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:stateValue;1",
      "@type": "Property",
      "displayName": {
        "en": "State"
      },
      "name": "stateValue",
      "schema": "string"
    },
    {
      "@id": "dtmi:azure:LocationManagement:LocationInformation:countryValue;1",
      "@type": "Property",
      "displayName": {
        "en": "Country"
      },
      "name": "countryValue",
      "schema": "string"
    }
  ],
  "displayName": {
    "en": "Location Information"
  },
  "@context": [
    "dtmi:iotcentral:context;2",
    "dtmi:dtdl:context;2"
  ]
}
```

6. Views: About Device

- About Device
    - Tile: Property - 2x2
    - Property:
        - Serial Number - Text
        - Device model - Text
        - Operating system name - Text
        - Software version - Text
        - Manufacturer - Text
        - Processor architecture - Text
        - Processor manufacturer - Text
    - Text size: 11pt

7. Views: Dashboard

- Heart Rate Monitor
    - Tile: Line chart 3x2
    - Display rage: Last 100 values
    - Telemetry:
        - HearRate
- Highest Heart Rate
    - Tile: Key Performance Indicator - 1x1
    - Time rage: Past 30 minutes
    - Telemetry:
        - HearRate - Maximum
    - Text size: 24pt
- Lowest Heart Rate
    - Tile: Key Performance Indicator - 1x1
    - Time rage: Past 30 minutes
    - Telemetry:
        - HearRate - Minimum
    - Text size: 24pt
- Average Heart Rate
    - Tile: Key Performance Indicator - 2x1
    - Time rage: Past 30 minutes
    - Telemetry:
        - HearRate - Average
    - Text size: 30pt
- Average Map
    - Tile: Heat map - 2x2
    - Time rage: Past 30 minutes
    - Telemetry:
        - HearRate - Average

9. Views: Emergency Centre

- Driver Information
    - Tile: Property - 3x2
    - Property:
        - Current Status - Text
        - Current Situation - Text
        - Driver Name - Text
        - Bloody Type - Text
        - Vehicle Registration Number - Text
        - Vehicle Manufacturer - Text
        - Vehicle Name - Text
    - Text size: 11pt
- Car Location
    - Tile: Map (property) - 2x2
    - Property:
        - Car Location
- Coordinates
    - Tile: Property - 2x2
    - Property:
        - Latitude - Text
        - Longitude - Text
        - Altitude - Text
        - Street - Text
        - City - Text
        - State - Text
        - Country - Text
    - Text size: 11pt

10. When you're done, please publish. Once published, Devices should also be set to "Heart Rate Checker" as a template.
11. If you create a new template, you need to set it up again in your Python code. Just copy Edit>Interface @id from
    template or get "@id" value at the top from Edit DTDL. There are 5 variables to `modify: model_id`
    , `heartRate_simulator_digital_model_identifier`, `device_info_digital_model_identifier`
    , `location_info_digital_model_identifie`, `driver_info_digital_model_identifier`. The following python file has
    that variable.

- heartarrest.py
- heartlow.py
- heartnormal.py
- hearttoolow.py
- locationhrarrest.py
- locationhrlow.py
- locationhrtoolow.py

## Additional IoT Central setting

Go to Rules and add two rules. Although there is an Emergency Center in the Devices, also try to set up an automatic
e-mail in case of an emergency.

1. Emergency Call: Cardiac arrest

- Taget Devices (Device templet)
    - Heart Rate Checker
- Conditions
    - Trigger the rule if
        - all of the conditions are ture
    - Time aggregation
        - Off
    - Condition
        - Telemetry
            - HeartRate
        - Operator
            - Equals
        - Value
            - Enter a value
                - 0
- Actions
    - Email
        - Display name
            - Emergency: Driver cardiac arrest
        - To
            - [Your e-mail]
        - Note
            - The driver is CARDIAC ARREST, this is an emergency situation now!

2. Emergency Call: Too low heart rate

- Taget Devices (Device templet)
    - Heart Rate Checker
- Conditions
    - Trigger the rule if
        - all of the conditions are ture
    - Time aggregation
        - Off
    - Condition 1
        - Telemetry
            - HeartRate
        - Operator
            - Is less than
        - Value
            - Enter a value
                - 40
    - Condition 2
        - Telemetry
            - HeartRate
        - Operator
            - Is greater than or equal to
        - Value
            - Enter a value
                - 1
- Actions
    - Email
        - Display name
            - Emergency: Driver lost consciousness
        - To
            - [Your e-mail]
        - Note
            - The driver is lost consciousness, this is dangerous now!

## Begin to the simulation

1. Run simulator `main.py`.

```shell
python3 main.py
```

2. When running for the first time, you need to Python dependency library and set the environment. If you have not done
   anything, proceed to steps 2, 3, and 4 in that order. If you only want to change the device in IoT Central, you only
   need to press 2 times to proceed.
3. First, press 2 to enter the IoT value you want to connect to. The value is obtained by pressing
   Devices>[Your Device]>
   Connect in IoT Central. Enter ID scope, Device ID and Primary key in order.
4. When step 2 is completed, press number 3 to add it to the system preferences. It is assumed that the default shell:
   Bash is used. If you are using a different shell, use the following command in the terminal.

```shell
# Example: when using zsh
echo 'source ~/.iot-hr-config' >> ~/.zshrc
```

5. If added successfully, you will need to restart .bashrc. Reload the system environment by typing `source ~/.bashrc`
   in the terminal or turn the terminal off and on. You can also open a new terminal.
6. Lastly, download the Python dependency libraries. Easy to install by pressing 4. Alternatively, you can install it
   manually with pip.

```shell
pip3 install -r requirements.txt
```

7. Note that step 2 can be done at any time when the device is changed. But, step 3 must be done only once.
8. When everything is set, press 1 to start!

## License

This code was created under the MIT license of Microsoft PnP sample code in Azure/azure-iot-sdk-python. This code is
also distributed under the same MIT license by leelsey(Heetak Yang). For more detail, please open the LICENSE file.
