# Yandex Smart Home CLI for OpenClaw

Python CLI для управления устройствами Яндекс Умного Дома из OpenClaw AI-ассистента.

## Возможности

- Управление лампами, люстрами, розетками, гирляндами
- Включение/выключение устройств
- Изменение яркости (0-100)
- Изменение цветовой температуры (1500-6500K)
- Установка цвета через HSV (Hue, Saturation, Value)
- JSON output для лёгкой интеграции

## Требования

- Python 3.8+
- OAuth токен Яндекса

## Установка

```bash
git clone https://github.com/wannawhat/openclaw-yandexiot.git
cd openclaw-yandexiot
python3 -m venv venv
source venv/bin/activate  # или venv/bin/activate на Windows
pip install -r requirements.txt
```

## Получение OAuth токена

1. Создайте приложение: https://oauth.yandex.ru/?dialog=create-client-entry (выберите "Для доступа к API или отладки")
2. Скопируйте `client_id`
3. Перейдите по ссылке авторизации:
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENT_ID
   ```
4. Скопируйте токен со страницы
5. Создайте файл `.env`:
   ```
   ya_oauth_token=ВАШ_ТОКЕН
   ```

## Использование

### Получить список устройств

```bash
python3 main.py get_all
```

Возвращает JSON с информацией о всех устройствах:

```json
[
  {
    "id": "1b82d50d-8662-44c2-a6ac-b53b8b5481f4",
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
]
```

### Включить/выключить

```bash
python3 main.py on <device_id>
python3 main.py off <device_id>
```

### Установить яркость

```bash
python3 main.py set <device_id> brightness 80
```

Значение: 0-100

### Установить цветовую температуру

```bash
python3 main.py set <device_id> temp 4000
```

Значение: 1500 (тёплый) - 6500 (холодный)

### Установить цвет

```bash
python3 main.py set <device_id> color 270 96 100
```

Параметры HSV:
- H (Hue): 0-360 (красный=0, синий=240, зелёный=120)
- S (Saturation): 0-100
- V (Value/Brightness): 0-100

## Интеграция с OpenClaw

Полная документация по интеграции находится в [SKILL.md](SKILL.md).

## Примеры сценариев

### Вечернее освещение

```bash
# Тёплый мягкий свет
python3 main.py set <device_id> brightness 30
python3 main.py set <device_id> temp 2700
```

### Рабочий режим

```bash
# Яркий холодный свет
python3 main.py set <device_id> brightness 100
python3 main.py set <device_id> temp 5000
```

### Цветная подсветка

```bash
# Фиолетовый
python3 main.py set <device_id> color 270 96 100

# Красный
python3 main.py set <device_id> color 0 100 100

# Синий
python3 main.py set <device_id> color 240 100 100
```

## Типы устройств

| Тип | Описание |
|-----|----------|
| `light` | Лампа / умная розетка с лампой |
| `light.ceiling` | Люстра |
| `light.strip` | Светодиодная лента |
| `light.garland` | Гирлянда |
| `socket` | Умная розетка |

## Output формат

Все команды возвращают JSON:

**Успех:**
```json
{"status": "ok"}
```

или

```json
{
  "status": "ok",
  "result": [...]
}
```

**Ошибка:**
```json
{
  "status": "error",
  "message": "описание ошибки"
}
```

## Автор

Создано [@wannawhat](https://github.com/wannawhat) для интеграции с [OpenClaw](https://github.com/openclaw/openclaw).

Интегрировано и поддерживается [Ray](https://github.com/rayxclaw) 🔦

## Лицензия

MIT
