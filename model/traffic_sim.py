import pygame
from model.car import Car
from model.driver import Driver

class TrafficSim:
    def __init__(self) -> None:
        self.drivers: [Driver] = []

    def update(self, dt: float) -> None:
        for driver in self.drivers:
            driver.update(dt)

    def draw(self, surface: pygame.Surface, debug: bool=False) -> None:
        for driver in self.drivers:
            driver.draw(surface, debug)

    def addDriver(self, driver: Driver) -> None:
        self.drivers.append(driver)