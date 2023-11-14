import time
from multiprocessing import Queue

import numpy as np

from sensor_headers import SensorHeaders


class QoSTracker:
    """
    Keeps track of running average processing times for each yolo-model.

    Fetches yolo-processed results from Kafka and updates the running average processing times to
    shared memory.

    As some models might not be in use for long durations, applies a decay over time to the running averages.
    """
    def __init__(self, queue: Queue, running_averages: dict):
        self.qos = {}
        self.qos_running_avg = running_averages
        self.qos_index = {}
        self.queue = queue
        self.max_processing_time_ms = 10000  # Hard limit for rolling averages (ms). Prevents too inflated values that take forever to decay. TODO: Make configurable
        self.array_length = 10  # Window length for rolling averages. TODO: Make configurable
        self.decay_per_second = 0.05  # Decay percentage per second for historical processing times. TODO: Make configurable
        self.verbose = True  # Increases amount of printing. TODO: Make configurable

    def start(self):
        self.tracking_loop()

    def tracking_loop(self):
        decay_timer = time.time()
        while True:
            try:
                data, headers_raw = self.queue.get_nowait()
            except:
                # Queue empty or closed
                data = None

            # Process data
            if data is not None:
                headers = SensorHeaders.from_bytes(headers_raw)
                processing_time_ms = (time.time_ns() - headers.timestamp) / 10**6
                if self.verbose:
                    print(f"[QoS] Received: {headers.model}, id: {headers.id}, "
                          f"total_processing_time: {processing_time_ms} ms")
                if headers.model not in self.qos.keys():
                    self.qos[headers.model] = np.zeros(self.array_length)
                    self.qos_running_avg[headers.model] = 0
                    self.qos_index[headers.model] = 0

                # TODO: Use a database for this...
                # Store processing time
                index = self.qos_index[headers.model]
                self.qos[headers.model][index] = min(processing_time_ms, self.max_processing_time_ms)
                # Increment index
                self.qos_index[headers.model] = (index + 1) % self.array_length

            # Process decay
            # We want the running avg to drop slowly if no new results are arriving
            for model in self.qos.keys():
                delta_time = time.time() - decay_timer
                self.qos[model] *= 1 - (delta_time * self.decay_per_second)
                decay_timer = time.time()

            # Compute running averages
            for model in self.qos.keys():
                self.qos_running_avg[model] = np.mean(self.qos[model])


