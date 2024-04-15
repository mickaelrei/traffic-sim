import pygame
from pygame.math import Vector2
from model.car import Car
from model.driver import Driver

# Main class for traffic simulation
class TrafficSim:
    def __init__(self) -> None:
        self.drivers: list[Driver] = []

    def update(self, dt: float) -> None:
        for driver in self.drivers:
            driver.update(dt, self.drivers)

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        for driver in self.drivers:
            driver.draw(surface, offset, debug)

    def addDriver(self, driver: Driver) -> None:
        self.drivers.append(driver)
