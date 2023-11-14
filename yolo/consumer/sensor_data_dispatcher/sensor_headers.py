import time


class SensorHeaders:
    def __init__(self, model_name, id, timestamp=None):
        self.model = model_name
        self.id = id
        if timestamp is None:
            self.timestamp = time.time_ns()
        else:
            self.timestamp = timestamp

    def to_bytes(self):
        return {
            "id": self.id.to_bytes(32, "big"),
            "model": bytes(self.model, 'utf-8'),
            "timestamp": self.timestamp.to_bytes(32, "big")
        }

    @classmethod
    def from_bytes(cls, headers_bytes):
        model = ""
        data_id = 0
        timestamp = 0
        for key, value in headers_bytes:
            if key == "model":
                model = value.decode("utf-8")
            elif key == "id":
                data_id = int.from_bytes(value, "big")
            elif key == "timestamp":
                timestamp = int.from_bytes(value, "big")
        return SensorHeaders(model, data_id, timestamp)
