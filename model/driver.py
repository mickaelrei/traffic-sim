import pygame
from model.car import Car

class Driver:
    def __init__(self, car: Car) -> None:
        self.car = car

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

        # Update car
        self.car.update(dt)

    def draw(self, surface: pygame.Surface, debug: bool=False) -> None:
        self.car.draw(surface, debug)