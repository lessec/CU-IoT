from azure.iot.device import Message
import json


class PnpProperties(object):
    def __init__(self, top_key, **kwargs):
        self._top_key = top_key
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def _to_value_dict(self):
        all_attrs = list((x for x in self.__dict__ if x != "_top_key"))
        inner = {key: {"value": getattr(self, key)} for key in all_attrs}
        return inner

    def _to_simple_dict(self):
        all_simple_attrs = list((x for x in self.__dict__ if x != "_top_key"))
        inner = {key: getattr(self, key) for key in all_simple_attrs}
        return inner


# Prepare to send the value generated as heart rate value in telemetry format to json
def create_telemetry(telemetry_msg, component_name=None):
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    if component_name:
        msg.custom_properties["$.sub"] = component_name
    return msg


# Create properties for devices
def create_reported_properties(component_name=None, **prop_kwargs):
    if component_name:
        print("\nUpdating Heart Rate properties for {component_name}".format(component_name=component_name))
    else:
        print("\nUpdating Heart Rate properties for root interface")
    prop_object = PnpProperties(component_name, **prop_kwargs)
    inner_dict = prop_object._to_simple_dict()
    if component_name:
        inner_dict["__t"] = "c"
        prop_dict = {}
        prop_dict[component_name] = inner_dict
    else:
        prop_dict = inner_dict

    print(prop_dict)
    return prop_dict

# Used when issuing commands from IoT Central
# It is installed by default, but it is not used in this simulation
def create_response_payload_with_status(command_request, method_name, create_user_response=None):
    if method_name:
        response_status = 200
    else:
        response_status = 404

    if not create_user_response:
        result = True if method_name else False
        data = "executed " + method_name if method_name else "unknown method"
        response_payload = {"result": result, "data": data}
    else:
        response_payload = create_user_response(command_request.payload)

    return (response_status, response_payload)


def create_reported_properties_from_desired(patch):
    print("\nthe data in the desired properties patch was: {}".format(patch))

    ignore_keys = ["__t", "$version"]
    component_prefix = list(patch.keys())[0]
    values = patch[component_prefix]
    print("\nValues received are :-")
    print(values)

    version = patch["$version"]
    inner_dict = {}

    for prop_name, prop_value in values.items():
        if prop_name in ignore_keys:
            continue
        else:
            inner_dict["ac"] = 200
            inner_dict["ad"] = "Successfully executed patch"
            inner_dict["av"] = version
            inner_dict["value"] = prop_value
            values[prop_name] = inner_dict

    properties_dict = dict()
    if component_prefix:
        properties_dict[component_prefix] = values
    else:
        properties_dict = values

    return properties_dict
