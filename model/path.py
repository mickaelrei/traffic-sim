import math
import pygame
from pygame.math import Vector2

# Path node color for debug rendering
PATH_NODE_COLOR = (255, 127, 0)

class Path:
    def __init__(self, nodes: list[Vector2]) -> None:
        self.nodes: list[Vector2] = nodes

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        if not debug: return

        for pos in self.nodes:
            pygame.draw.circle(surface, PATH_NODE_COLOR, pos + offset, 5)