from enum import Enum

class StatusEnum(str, Enum):
    online = "online"
    away = "away"
    busy = "busy"
    not_visible = "not_visible"