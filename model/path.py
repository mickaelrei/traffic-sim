import math
import pygame
from pygame.math import Vector2

class Path:
    def __init__(self, nodes: list[Vector2]) -> None:
        self.nodes: list[Vector2] = nodes

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        if not debug: return

        for pos in self.nodes:
            pygame.draw.circle(surface, (255, 127, 0), pos + offset, 5)