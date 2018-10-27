import math
import random
from typing import Tuple

import noise

ZONES = {
    "S": (0.0, 0.3),  # Snow
    "F": (0.3, 0.4),  # Forest
    "P": (0.4, 0.7),  # Forest
    "D": (0.7, 1.0)  # Desert
}


def get_for_noise(noise_val):
    noise_val += 1.0
    noise_val /= 2.0
    noise_val = max(0.00, noise_val)
    noise_val = min(0.99, noise_val)

    for zone, temperature in ZONES.items():
        if temperature[0] <= noise_val < temperature[1]:
            return zone


def noise_octave(noise_func=None, octaves: int = 1, persistence: float = 1.0, coordinates: Tuple[float, ...] = ()):
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    for _ in range(octaves):
        noise_value = noise_func(*tuple(coord * frequency for coord in coordinates)) * amplitude
        total += noise_value
        max_value += amplitude

        amplitude *= persistence
        frequency *= 2

    return total / max_value


def generate_terrain(dimensions, zone_size=15, spawn_range=50, seed=None):
    map_middle = dimensions // 2
    map = [["?" for x in range(dimensions)] for y in range(dimensions)]

    if not seed:
        seed = random.randrange(-1000, 1000)

    for x in range(dimensions):
        for y in range(dimensions):
            map[y][x] = get_for_noise(
                noise_octave(
                    noise_func=noise.snoise3,
                    octaves=2,
                    persistence=0.1,
                    coordinates=(x / 15, y / 15, seed)
                )
            )

            # Since we want to avoid having a lot of water near the spawn range, we can use
            # a down-pointing elliptic paraboloid to represent the probability of a river at
            # that position.

            # This is all ad-hoc. Not a lot of thought went into the math.

            # check if the coordinates are within the spawn range (pythagoras theorem)
            max_noise_range = 0.2
            within_spawn_range = spawn_range < math.sqrt((x - map_middle) ** 2 + (y - map_middle) ** 2)
            if within_spawn_range:
                max_noise_range = ((x ** 2) / 16 + (y ** 2) / 16) / 1000
            river_val = noise_octave(
                noise_func=noise.snoise3,
                octaves=1,
                persistence=2,
                coordinates=(x / 15, y / 15, seed)
            )

            if max_noise_range > river_val > 0.0:
                map[y][x] = "W"
    return map
