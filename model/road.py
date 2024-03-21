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

# General curved road, can pass any angle
class CurvedRoad(Road):
    def __init__(self, width: float, center: Vector2, arcOffset: float, curveAngle: float) -> None:
        super().__init__(width)
        self.center = center
        self.arcOffset = arcOffset
        self.curveAngle = curveAngle

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        # Get initial and final arc angle
        # -------------------------------
        initialAngle = self.curveAngle - math.pi / 4
        finalAngle = initialAngle + math.pi / 2

        # Calculate rect center and size for outer arc
        # --------------------------------------------
        rectSize = 2 * (self.width + self.arcOffset)
        centerOffsetLength = math.sqrt(2) * (self.width + self.arcOffset / 2)
        rect = pygame.Rect(0, 0, rectSize, rectSize)
        c = math.cos(self.curveAngle)
        s = math.sin(self.curveAngle)
        rect.center = (
            self.center.x - c * centerOffsetLength + offset.x,
            self.center.y + s * centerOffsetLength + offset.y
        )
        # Draw outer arc
        # pygame.draw.rect(surface, (255, 0, 0), rect, 1)
        pygame.draw.arc(surface, ROAD_OUTLINE_COLOR, rect, initialAngle, finalAngle, 1)

        # Calculate rect center and size for inner arc
        # --------------------------------------------
        rectSize = self.width + self.arcOffset
        rect.size = (rectSize, rectSize)
        rect.center = (
            self.center.x - c * centerOffsetLength + offset.x,
            self.center.y + s * centerOffsetLength + offset.y
        )
        # pygame.draw.rect(surface, (0, 255, 0), rect, 1)
        pygame.draw.arc(surface, ROAD_OUTLINE_COLOR, rect, initialAngle, finalAngle, 1)

        # Calculate rect center and size for middle yellow stripe arc
        # -----------------------------------------------------------
        rectSize = self.width + self.arcOffset * 2
        rect.size = (rectSize, rectSize)
        rect.center = (
            self.center.x - c * centerOffsetLength + offset.x,
            self.center.y + s * centerOffsetLength + offset.y
        )
        # pygame.draw.rect(surface, (0, 255, 0), rect, 1)
        pygame.draw.arc(surface, ROAD_YELLOW_STRIPE_COLOR, rect, initialAngle, finalAngle, 1)

# Specialization of CurvedRoad with defined angle
class TopLeftCurvedRoad(CurvedRoad):
    # Class for a road that does a curve from north to west (top to left)
    def __init__(self, width: float, center: Vector2, arcOffset: float) -> None:
        super().__init__(width, center, arcOffset, math.pi / 4)

# Specialization of CurvedRoad with defined angle
class TopRightCurvedRoad(CurvedRoad):
    # Class for a road that does a curve from north to east (top to right)
    def __init__(self, width: float, center: Vector2, arcOffset: float) -> None:
        super().__init__(width, center, arcOffset, 3 * math.pi / 4)

# Specialization of CurvedRoad with defined angle
class BottomLeftCurvedRoad(CurvedRoad):
    # Class for a road that does a curve from south to west (bottom to left)
    def __init__(self, width: float, center: Vector2, arcOffset: float) -> None:
        super().__init__(width, center, arcOffset, -math.pi / 4)

# Specialization of CurvedRoad with defined angle
class BottomRightCurvedRoad(CurvedRoad):
    # Class for a road that does a curve from south to east (bottom to right)
    def __init__(self, width: float, center: Vector2, arcOffset: float) -> None:
        super().__init__(width, center, arcOffset, 5 * math.pi / 4)