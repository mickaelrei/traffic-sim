import pygame
import math
from pygame.math import Vector2

# Color of road outlines
ROAD_OUTLINE_COLOR = (140, 140, 140)

# Color of road middle yellow stripes
ROAD_YELLOW_STRIPE_COLOR = (140, 140, 0)


class Road:
    # Abstract class that defines a road object
    def __init__(self, width: float) -> None:
        self.width = width

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        pass


class StraightRoad(Road):
    # Class for straight road, with given start and end
    def __init__(self, width: float, start: Vector2, end: Vector2) -> None:
        super().__init__(width)
        self.start = start
        self.end = end

        # If start and end are the same, can't calculate direction
        if start == end:
            self.direction = None
            return

        # Calculate road angle, direction and normal
        self.direction = (end - start).normalize()
        self.normal = Vector2(-self.direction.y, self.direction.x)
        self.angle = math.atan2(self.direction.y, self.direction.x)

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        # Check if direction exists (start and end are different points)
        if self.direction == None:
            return

        # Define 4 road corners
        # ---------------------
        halfNormal = self.normal * self.width / 2
        startTop = self.start - halfNormal
        startBottom = self.start + halfNormal
        endTop = self.end - halfNormal
        endBottom = self.end + halfNormal

        # Outline
        # -------
        pygame.draw.line(surface, ROAD_OUTLINE_COLOR,
                         startTop + offset, endTop + offset, 1)
        pygame.draw.line(surface, ROAD_OUTLINE_COLOR,
                         startBottom + offset, endBottom + offset, 1)

        # Middle yellow stripe
        # --------------------
        pygame.draw.line(surface, ROAD_YELLOW_STRIPE_COLOR,
                         self.start + offset, self.end + offset)


class CurveRoad(Road):
    # Class for a curve road, with start-end positions and angles
    def __init__(self, width: float, startPos: Vector2, endPos: Vector2, startAngle: float, endAngle: float) -> None:
        super().__init__(width)
        self.startPos = startPos
        self.endPos = endPos
        self.startAngle = startAngle
        self.endAngle = endAngle

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        # TODO: Draw inside arc, outside arc and middle yellow stripe arc
        pass
