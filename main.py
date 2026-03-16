import sys
import json
import os
from dotenv import load_dotenv
from ya_api import YaApi

load_dotenv()

USAGE = """
Yandex Smart Home CLI

COMMANDS:
  get_all                          — список всех ламп и розеток с состоянием
  on  <device_id>                  — включить
  off <device_id>                  — выключить
  set <device_id> brightness <0-100>
  set <device_id> temp <1500-6500>
  set <device_id> color <h> <s> <v>
""".strip()


def ok(data: dict | list | None = None):
    if data is not None:
        print(json.dumps({"status": "ok", "result": data}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "ok"}, ensure_ascii=False))


def err(message: str):
    print(json.dumps({"status": "error", "message": message}, ensure_ascii=False))
    sys.exit(1)


def main():
    token = os.environ.get("ya_oauth_token")
    if not token:
        err("ya_oauth_token not set in .env")

    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(0)

    api = YaApi(token)
    cmd = args[0]

    if cmd == "get_all":
        user_info = api.get_user_info()
        ok(user_info.get_lights_and_sockets())

    elif cmd == "on":
        if len(args) < 2:
            err("Usage: on <device_id>")
        api.set_on_off(args[1], True)
        ok()

    elif cmd == "off":
        if len(args) < 2:
            err("Usage: off <device_id>")
        api.set_on_off(args[1], False)
        ok()

    elif cmd == "set":
        if len(args) < 3:
            err("Usage: set <device_id> <brightness|temp|color> [values...]")
        device_id = args[1]
        prop = args[2]

        if prop == "brightness":
            if len(args) < 4:
                err("Usage: set <device_id> brightness <0-100>")
            api.set_brightness(device_id, int(args[3]))

        elif prop == "temp":
            if len(args) < 4:
                err("Usage: set <device_id> temp <1500-6500>")
            api.set_color_temp(device_id, int(args[3]))

        elif prop == "color":
            if len(args) < 6:
                err("Usage: set <device_id> color <h 0-360> <s 0-100> <v 0-100>")
            api.set_color(device_id, int(args[3]), int(args[4]), int(args[5]))

        else:
            err(f"Unknown property '{prop}'. Use: brightness, temp, color")
        ok()

    else:
        err(f"Unknown command '{cmd}'. Run without args to see usage.")


if __name__ == "__main__":
    main()
