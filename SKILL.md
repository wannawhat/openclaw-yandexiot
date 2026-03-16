# Yandex Smart Home Skill

Этот скилл позволяет управлять устройствами умного дома Яндекс: лампами и розетками.

## Установка (выполнить один раз)

Требования: **python3**, pip

```bash
# Клонируем в workspace tools
cd /root/.openclaw/workspace/tools
git clone https://github.com/wannawhat/openclaw-yandexiot yandex-home
cd yandex-home

# Создаём venv и ставим зависимости
python3 -m venv venv
venv/bin/pip install requests python-dotenv pydantic
```

### Авторизация

Для работы нужен OAuth токен Яндекса. Веди пользователя по шагам:

1. Попроси перейти по ссылке и создать приложение (выбрать пункт "Для доступа к API или отладки"):
   ```
   https://oauth.yandex.ru/?dialog=create-client-entry
   ```
   После создания попросить сообщить `client_id`.

2. Подставь `client_id` в ссылку и попроси пользователя перейти по ней:
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}
   ```

3. После авторизации на странице будет написан токен — попроси его скопировать и прислать.

4. Создай файл `.env` в папке проекта:
   ```
   ya_oauth_token=ТОКЕН_СЮДА
   ```

### Проверка установки

```bash
cd /root/.openclaw/workspace/tools/yandex-home
venv/bin/python3 main.py get_all
```

Если вернулся JSON со списком устройств — всё готово.

**Важно:** всегда используй полные пути к device_id (не работают сокращённые ID вида `1b82d50d`). Сначала вызывай `get_all`, чтобы получить полные ID.

---

## Команды

### Получить список устройств

```bash
python3 main.py get_all
```

Возвращает JSON-массив. Каждый объект:

```json
{
  "id": "1b82d50d-...",
  "name": "Светильник",
  "room": "Спальня",
  "type": "light.ceiling",
  "state": {
    "on": true,
    "brightness": 100,
    "temp": 4500
  },
  "can": ["on_off", "brightness", "temp", "color"]
}
```

Поле `can` — список того, чем можно управлять у данного устройства.

### Включить / выключить

```bash
python3 main.py on  <device_id>
python3 main.py off <device_id>
```

### Изменить свойства (`can` должно содержать нужное свойство)

```bash
# Яркость: 0–100
python3 main.py set <device_id> brightness 80

# Цветовая температура: 1500 (тёплый) — 6500 (холодный)
python3 main.py set <device_id> temp 4000

# Цвет HSV: H=0-360, S=0-100, V=0-100
python3 main.py set <device_id> color 270 96 100
```

---

## Вывод

Все команды возвращают JSON:

- Успех: `{"status": "ok"}` или `{"status": "ok", "result": [...]}`
- Ошибка: `{"status": "error", "message": "описание"}`

---

## Примеры сценариев

**Выключить весь свет в спальне:**
1. Запусти `get_all`
2. Найди устройства с `"room": "Спальня"` и `"on": true`
3. Для каждого выполни `off <id>`

**Установить вечернее освещение:**
```bash
python3 main.py set 1b82d50d-... brightness 30
python3 main.py set 1b82d50d-... temp 2700
```

**Включить цветную подсветку (лиловый):**
```bash
python3 main.py set e5a391fe-... color 270 96 100
```

---

## Типы устройств

| type           | описание          |
|----------------|-------------------|
| `light`        | лампа / умная розетка с лампой |
| `light.ceiling`| люстра            |
| `light.strip`  | светодиодная лента|
| `light.garland`| гирлянда          |
| `socket`       | умная розетка     |

## Свойства (`can`)

| свойство     | команда       | значения            |
|--------------|---------------|---------------------|
| `on_off`     | `on` / `off`  | —                   |
| `brightness` | `set brightness` | 0–100            |
| `temp`       | `set temp`    | 1500–6500           |
| `color`      | `set color`   | H 0-360, S 0-100, V 0-100 |
