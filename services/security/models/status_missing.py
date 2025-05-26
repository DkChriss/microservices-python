from enum import Enum

class StatusMissingEnum(str, Enum):
    pending = "pending"
    progress = "progress"
    suspended = "suspended"
    resumed = "resumed"
    completed = "completed"