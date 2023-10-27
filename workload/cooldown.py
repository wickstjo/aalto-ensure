import matplotlib.pyplot as plt
import math
import time

# GET ACTION COOLDOWN BASED ON TIMESTAMP+SINE WAVE
def generate_cooldown(bonus=0):

    # STATIC VARS
    frequency = 0.5
    oscillation = 4
    buffer = 0.3

    # FETCH SIN-WAVE COOLDOWN
    return (0.2 * math.sin((time.time() + bonus) * frequency * math.pi / 60) + buffer) * oscillation

# GRAPH COOLDOWN SINE WAVE
def cooldown_sim(n=500):
    sin_data = []

    for b in range(n):
        value = generate_cooldown(b)
        sin_data.append(value)

    print('N:\t', len(sin_data))
    print('MIN:\t', min(sin_data))
    print('MAX:\t', max(sin_data))
    
    plt.plot([x for x in range(len(sin_data))], sin_data)

# print(generate_cooldown())
# cooldown_sim()