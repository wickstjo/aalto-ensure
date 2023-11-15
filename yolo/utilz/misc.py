import bezier, datetime
import numpy as np
import matplotlib.pyplot as plt
import json

class DayNightCycle:
    def __init__(self):
        self.traffic_stats = [
            # (name, time (24h), value, tangent_offset)
            ("night", 0.0, 20, 7.0),
            ("morning_peak", 8.0, 80, 1.0),
            ("day", 12.0, 50, 2.0),
            ("evening_peak", 17.0, 100, 3),
            ("night", 24.0, 20, 2),
        ]
        self.curves = []
        for i in range(len(self.traffic_stats) - 1):
            name, time1, value1, off1 = self.traffic_stats[i]
            name, time2, value2, off2 = self.traffic_stats[i+1]
            # offset = (time2-time1)/2
            # offset = off1
            # print(f"{name}, offset:{offset}")
            curve_nodes = np.asfortranarray([
                [time1, time1+off1, time2-off2, time2],   # x-axis
                [value1, value1, value2, value2],   # y-axis
            ])
            curve = bezier.Curve(curve_nodes, degree=3)
            self.curves.append(curve)

    def evaluate(self, time, verbose=False):
        # Input: time between [0,24] (24h time)
        # Output: y value for curve at given time
        for i in range(len(self.traffic_stats)-1):
            name1, time1, value1, off1 = self.traffic_stats[i]
            name2, time2, value2, off2 = self.traffic_stats[i+1]
            if time >= time1 and time <= time2:
                length = time2-time1
                t = (time - time1) / length
                # print(f"{time} - {time1}")
                x, y = self.curves[i].evaluate(t)
                if verbose:
                    print(f"{name1}, time:{time}, t:{ (time - time1)}, t_norm: {t}, val:{y}")
                return y / 100
        print(f"WARNING: time {time} out of scope! Expected value between 0 and 24.")
        return 0

    def plot(self):
        fig, ax = plt.subplots()
        for curve in self.curves:
            curve.plot(100, ax=ax)
            # self.curve2.plot(100, ax=ax)
        plt.title("City traffic - Day-night cycle (24h)")
        plt.xlabel("Time of day (hours)")
        plt.ylabel("Traffic intensity (%)")
        plt.xlim([0, 25])
        plt.ylim([0, 110])


# if __name__ == "__main__":
#     cycle = DayNightCycle()
#     cycle.plot()
#     plt.show()
#     for i in range(25):
#         cycle.evaluate(i)

def get_formatted_time():
    now = datetime.datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
    return formatted_date

# DESERIALIZE BYTES DATA -- INVERSE OF THE PRODUCERS SERIALIZER
def custom_deserializer(raw_bytes):
    return json.loads(raw_bytes.decode('UTF-8'))

# CUSTOM DATA => BYTES SERIALIZED -- INVERSE OF THE CONSUMERS DESERIALIZER
def custom_serializer(data):
    return json.dumps(data).encode('UTF-8')