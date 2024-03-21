import pygame
from pygame.math import Vector2
import math
from model.car import Car

class Driver:
    def __init__(self, car: Car) -> None:
        self.car = car
        self.elapsedTime = 0

    def update(self, dt: float) -> None:
        # TODO: Set car stats with methods such as:
        # - setSteering
        # - setAccelerationAmount
        # - setBrakeAmount
        #
        # Based on info such as:
        # - Cars in front
        # - Current path trajectory
        # - Traffic lights

        self.elapsedTime += dt
        acc = math.sin(self.elapsedTime) / 2 + 0.5
        brake = math.sin(self.elapsedTime / 4 + math.pi * 1.5) / 4 + 0.25
        self.car.setAccelerationAmount(1 - acc ** 2)
        self.car.setBrakeAmount(brake ** 2)
        self.car.setSteering(math.cos(self.elapsedTime))

        # Update car
        self.car.update(dt)

    def draw(self, surface: pygame.Surface, offset: Vector2=Vector2(0, 0), debug: bool=False) -> None:
        self.car.draw(surface, offset, debug)