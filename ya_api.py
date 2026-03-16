import requests
from pydantic import BaseModel
from typing import Any

LIGHT_SOCKET_TYPES = {
    "devices.types.light",
    "devices.types.light.ceiling",
    "devices.types.light.strip",
    "devices.types.light.garland",
    "devices.types.socket",
}


class DeviceInfo(BaseModel):
    manufacturer: str | None = None
    model: str | None = None


class CapabilityState(BaseModel):
    instance: str
    value: Any


class Capability(BaseModel):
    type: str
    retrievable: bool = False
    reportable: bool = False
    parameters: dict = {}
    state: CapabilityState | None = None


class PropertyState(BaseModel):
    instance: str
    value: Any


class Property(BaseModel):
    type: str
    retrievable: bool = False
    reportable: bool = False
    state: PropertyState | None = None


class Device(BaseModel):
    id: str
    name: str
    type: str
    household_id: str
    room: str | None = None
    aliases: list[str] = []
    capabilities: list[Capability] = []
    properties: list[Property] = []
    device_info: DeviceInfo | None = None

    def to_compact(self, room_name: str | None) -> dict:
        short_type = self.type.replace("devices.types.", "")
        state: dict = {}
        can: list[str] = []

        for cap in self.capabilities:
            if cap.type == "devices.capabilities.on_off":
                can.append("on_off")
                if cap.state:
                    state["on"] = cap.state.value

            elif cap.type == "devices.capabilities.range":
                if cap.state and cap.state.instance == "brightness":
                    can.append("brightness")
                    state["brightness"] = cap.state.value

            elif cap.type == "devices.capabilities.color_setting":
                if "temperature_k" in cap.parameters:
                    can.append("temp")
                if cap.parameters.get("color_model") == "hsv":
                    can.append("color")

                if cap.state:
                    if cap.state.instance == "temperature_k":
                        state["temp"] = cap.state.value
                    elif cap.state.instance == "hsv":
                        v = cap.state.value
                        state["color"] = [v["h"], v["s"], v["v"]]

        return {
            "id": self.id,
            "name": self.name,
            "room": room_name,
            "type": short_type,
            "state": state,
            "can": can,
        }

    def display(self) -> str:
        lines = [f"  [{self.type}] {self.name}"]
        lines.append(f"    id: {self.id}")
        if self.room:
            lines.append(f"    room: {self.room}")
        if self.device_info:
            lines.append(f"    device: {self.device_info.manufacturer} {self.device_info.model}")
        for cap in self.capabilities:
            state_str = ""
            if cap.state:
                state_str = f" = {cap.state.value}"
            lines.append(f"    capability: {cap.state.instance if cap.state else cap.type}{state_str}")
        for prop in self.properties:
            if prop.state:
                lines.append(f"    property: {prop.state.instance} = {prop.state.value}")
        return "\n".join(lines)


class UserInfo(BaseModel):
    rooms: list[dict] = []
    devices: list[Device] = []
    households: list[dict] = []

    def get_room_name(self, room_id: str | None) -> str | None:
        if not room_id:
            return None
        for room in self.rooms:
            if room["id"] == room_id:
                return room["name"]
        return None

    def get_lights_and_sockets(self) -> list[dict]:
        return [
            d.to_compact(self.get_room_name(d.room))
            for d in self.devices
            if d.type in LIGHT_SOCKET_TYPES
        ]

    def print_devices(self):
        by_household: dict[str, list[Device]] = {}
        for device in self.devices:
            by_household.setdefault(device.household_id, []).append(device)

        household_names = {h["id"]: h["name"] for h in self.households}

        for household_id, devices in by_household.items():
            name = household_names.get(household_id, household_id)
            print(f"\n=== {name} ({len(devices)} devices) ===")

            by_room: dict[str | None, list[Device]] = {}
            for device in devices:
                room_name = self.get_room_name(device.room)
                by_room.setdefault(room_name, []).append(device)

            for room_name, room_devices in by_room.items():
                print(f"\n  -- {room_name or 'Без комнаты'} --")
                for device in room_devices:
                    print(device.display())


class YaApi:
    BASE_URL = "https://api.iot.yandex.net"

    def __init__(self, ya_oauth_token: str):
        self.ya_oauth_token = ya_oauth_token

    def _get(self, path: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"OAuth {self.ya_oauth_token}"}
        )
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                raise Exception(f"Error parsing response: {e}, {response.text}")
        else:
            raise Exception(f"Error calling {path}: {response.status_code}, {response.text}")

    def _post(self, path: str, body: dict) -> dict:
        response = requests.post(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"OAuth {self.ya_oauth_token}"},
            json=body,
        )
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                raise Exception(f"Error parsing response: {e}, {response.text}")
        else:
            raise Exception(f"Error calling {path}: {response.status_code}, {response.text}")

    def _action(self, device_id: str, capability_type: str, instance: str, value: Any) -> dict:
        return self._post("/v1.0/devices/actions", {
            "devices": [{
                "id": device_id,
                "actions": [{
                    "type": capability_type,
                    "state": {"instance": instance, "value": value},
                }],
            }]
        })

    def get_user_info(self) -> UserInfo:
        return UserInfo.model_validate(self._get("/v1.0/user/info"))

    def get_devices(self) -> list[Device]:
        return self.get_user_info().devices

    def get_device(self, device_id: str) -> dict:
        return self._get(f"/v1.0/devices/{device_id}")

    def set_on_off(self, device_id: str, on: bool) -> dict:
        return self._action(device_id, "devices.capabilities.on_off", "on", on)

    def set_brightness(self, device_id: str, value: int) -> dict:
        return self._action(device_id, "devices.capabilities.range", "brightness", value)

    def set_color_temp(self, device_id: str, value: int) -> dict:
        return self._action(device_id, "devices.capabilities.color_setting", "temperature_k", value)

    def set_color(self, device_id: str, h: int, s: int, v: int) -> dict:
        return self._action(device_id, "devices.capabilities.color_setting", "hsv", {"h": h, "s": s, "v": v})
