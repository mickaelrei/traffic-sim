import math
import pygame
from pygame.math import Vector2
import utils

class PathNode:
    def __init__(self, pos: Vector2, angle: float) -> None:
        self.pos = pos
        self.angle = utils.normalizeAngle(angle)

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        # Offset position
        pos = self.pos + offset

        # Circle at position
        pygame.draw.circle(surface, (255, 127, 0), pos, 5)

        # Arrow pointing in direction of angle
        if debug:
            direc = utils.directionVector(self.angle)
            utils.drawArrow(surface, pos, pos + direc * 25)

class Path:
    def __init__(self, nodes: list[PathNode]) -> None:
        self.nodes = nodes

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        for i, node in enumerate(self.nodes):
            node.draw(surface, offset, debug)
            if debug:
                utils.drawText(surface, f'Node {i}', node.pos + offset, anchorY=1)