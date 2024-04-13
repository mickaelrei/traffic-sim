import pygame
import math
import utils
from pygame.math import Vector2

# Color of road outlines
ROAD_OUTLINE_COLOR = (140, 140, 140)

# Color of road middle yellow stripes
ROAD_YELLOW_STRIPE_COLOR = (140, 140, 0)

ROAD_OUTLINE_WIDTH = 3


# Abstract class road
class Road:
    # Abstract class that defines a road object
    def __init__(self, width: float) -> None:
        self.width = width

    def draw(
        self,
        surface: pygame.Surface,
        offset: Vector2 = Vector2(0, 0),
        debug: bool = False,
    ) -> None:
        pass


# Straight road, with start and end points
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
        self.angle = utils.angleFromDirection(self.direction)

    def draw(
        self,
        surface: pygame.Surface,
        offset: Vector2 = Vector2(0, 0),
        debug: bool = False,
    ) -> None:
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
        pygame.draw.line(
            surface,
            ROAD_OUTLINE_COLOR,
            startTop + offset,
            endTop + offset,
            ROAD_OUTLINE_WIDTH,
        )
        pygame.draw.line(
            surface,
            ROAD_OUTLINE_COLOR,
            startBottom + offset,
            endBottom + offset,
            ROAD_OUTLINE_WIDTH,
        )

        # Middle yellow stripe
        # --------------------
        pygame.draw.line(
            surface,
            ROAD_YELLOW_STRIPE_COLOR,
            self.start + offset,
            self.end + offset,
            ROAD_OUTLINE_WIDTH,
        )


# General curved road, can pass any angle
class CurvedRoad(Road):
    def __init__(
        self, width: float, center: Vector2, arcOffset: float, curveAngle: float
    ) -> None:
        super().__init__(width)
        self.center = center
        self.arcOffset = arcOffset
        self.curveAngle = curveAngle

        # Cache some variables that get used on draw and never change
        self.cos = math.cos(self.curveAngle)
        self.sin = math.sin(self.curveAngle)
        self.initialAngle = self.curveAngle - math.pi / 4
        self.finalAngle = self.initialAngle + math.pi / 2

    def draw(
        self,
        surface: pygame.Surface,
        offset: Vector2 = Vector2(0, 0),
        debug: bool = False,
    ) -> None:
        if debug:
            pygame.draw.circle(
                surface,
                (255, 0, 0),
                self.center + offset,
                10,
                1,
            )

        # Calculate center and size for outer arc
        # --------------------------------------------
        offsetLength = math.sqrt(2) * (self.width / 2 + self.arcOffset)
        center = Vector2(
            self.center.x - self.cos * offsetLength,
            self.center.y - self.sin * offsetLength,
        )
        # Draw outer arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            center + offset,
            Vector2(self.width + self.arcOffset),
            self.initialAngle,
            self.finalAngle,
            ROAD_OUTLINE_WIDTH,
        )

        # Calculate center and size for inner arc
        # --------------------------------------------
        offsetLength = math.sqrt(2) * (self.width / 2 + self.arcOffset)
        center = Vector2(
            self.center.x - self.cos * offsetLength,
            self.center.y - self.sin * offsetLength,
        )
        # Draw inner arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            center + offset,
            Vector2(self.arcOffset),
            self.initialAngle,
            self.finalAngle,
            ROAD_OUTLINE_WIDTH,
        )

        # Calculate center and size for middle yellow stripe arc
        # -----------------------------------------------------------
        offsetLength = math.sqrt(2) * (self.width / 2 + self.arcOffset)
        center = Vector2(
            self.center.x - self.cos * offsetLength,
            self.center.y - self.sin * offsetLength,
        )
        # Draw middle yellow stripe arc
        utils.drawArc(
            surface,
            ROAD_YELLOW_STRIPE_COLOR,
            center + offset,
            Vector2(self.width / 2 + self.arcOffset),
            self.initialAngle,
            self.finalAngle,
            ROAD_OUTLINE_WIDTH,
        )


# Roundabout road, with possible connections on top, bottom, left and right
class Roundabout(Road):
    def __init__(
        self,
        width: float,
        center: Vector2,
        connectTop: bool = False,
        connectBottom: bool = False,
        connectLeft: bool = False,
        connectRight: bool = False,
    ) -> None:
        super().__init__(width)
        self.center = center
        self.connectBottom = connectBottom
        self.connectTop = connectTop
        self.connectLeft = connectLeft
        self.connectRight = connectRight

    def draw(
        self,
        surface: pygame.Surface,
        offset: Vector2 = Vector2(0, 0),
        debug: bool = False,
    ) -> None:
        arcOffset = self.width / 10
        sizeMult = 2
        size = Vector2(self.width * sizeMult)
        offsetAngle = math.asin((self.width / 2 + arcOffset) / (self.width * sizeMult))

        # Top left arc
        # ------------
        startAngle = math.pi
        endAngle = 3 * math.pi / 2
        if self.connectTop:
            endAngle -= offsetAngle
        if self.connectLeft:
            startAngle += offsetAngle
        # Outine arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            offset + self.center,
            size,
            startAngle,
            endAngle,
            ROAD_OUTLINE_WIDTH,
        )
        if self.connectLeft:
            # Arc to connect to road on left
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(-arcOffset, 0)
                + utils.directionVector(startAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                0,
                math.pi / 2,
                ROAD_OUTLINE_WIDTH,
            )
        if self.connectTop:
            # Arc to connect to road on top
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(0, -arcOffset)
                + utils.directionVector(endAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                0,
                math.pi / 2,
                ROAD_OUTLINE_WIDTH,
            )

        # Bottom left arc
        # ------------
        startAngle = math.pi / 2
        endAngle = math.pi
        if self.connectLeft:
            endAngle -= offsetAngle
        if self.connectBottom:
            startAngle += offsetAngle
        # Outline arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            offset + self.center,
            size,
            startAngle,
            endAngle,
            ROAD_OUTLINE_WIDTH,
        )
        if self.connectBottom:
            # Arc to connect to road on bottom
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(0, arcOffset)
                + utils.directionVector(startAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                3 * math.pi / 2,
                0,
                ROAD_OUTLINE_WIDTH,
            )
        if self.connectLeft:
            # Arc to connect to road on left
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(-arcOffset, 0)
                + utils.directionVector(endAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                3 * math.pi / 2,
                0,
                ROAD_OUTLINE_WIDTH,
            )

        # Bottom right arc
        # ------------
        startAngle = 0
        endAngle = math.pi / 2
        if self.connectBottom:
            endAngle -= offsetAngle
        if self.connectRight:
            startAngle += offsetAngle
        # Outline arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            offset + self.center,
            size,
            startAngle,
            endAngle,
            ROAD_OUTLINE_WIDTH,
        )
        if self.connectRight:
            # Arc to connect to road on right
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(arcOffset, 0)
                + utils.directionVector(startAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                math.pi,
                3 * math.pi / 2,
                ROAD_OUTLINE_WIDTH,
            )
        if self.connectBottom:
            # Arc to connect to road on bottom
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(0, arcOffset)
                + utils.directionVector(endAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                math.pi,
                3 * math.pi / 2,
                ROAD_OUTLINE_WIDTH,
            )

        # Top right arc
        # ------------
        startAngle = 3 * math.pi / 2
        endAngle = 0
        if self.connectRight:
            endAngle -= offsetAngle
        if self.connectTop:
            startAngle += offsetAngle
        # Outline arc
        utils.drawArc(
            surface,
            ROAD_OUTLINE_COLOR,
            offset + self.center,
            size,
            startAngle,
            endAngle,
            ROAD_OUTLINE_WIDTH,
        )
        if self.connectTop:
            # Arc to connect to road on top
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(0, -arcOffset)
                + utils.directionVector(startAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                math.pi / 2,
                math.pi,
                ROAD_OUTLINE_WIDTH,
            )
        if self.connectRight:
            # Arc to connect to road on right
            utils.drawArc(
                surface,
                ROAD_OUTLINE_COLOR,
                offset
                + self.center
                + Vector2(arcOffset, 0)
                + utils.directionVector(endAngle) * self.width * sizeMult,
                Vector2(arcOffset),
                math.pi / 2,
                math.pi,
                ROAD_OUTLINE_WIDTH,
            )

        # Inner road outline
        pygame.draw.circle(
            surface,
            ROAD_OUTLINE_COLOR,
            offset + self.center,
            self.width * (sizeMult - 1 / 2),
            ROAD_OUTLINE_WIDTH,
        )


# Curved road for a turn from north to west (top to left)
def topLeftCurvedRoad(
    width: float,
    center: Vector2,
    arcOffset: float,
) -> CurvedRoad:
    return CurvedRoad(width, center, arcOffset, -math.pi / 4)


# Curved road for a turn from north to east (top to right)
def topRightCurvedRoad(
    width: float,
    center: Vector2,
    arcOffset: float,
) -> CurvedRoad:
    return CurvedRoad(width, center, arcOffset, 5 * math.pi / 4)


# Curved road for a turn from south to west (bottom to left)
def bottomLeftCurvedRoad(
    width: float,
    center: Vector2,
    arcOffset: float,
) -> CurvedRoad:
    return CurvedRoad(width, center, arcOffset, math.pi / 4)


# Curved road for a turn from south to east (bottom to right)
def bottomRightCurvedRoad(
    width: float,
    center: Vector2,
    arcOffset: float,
) -> CurvedRoad:
    return CurvedRoad(width, center, arcOffset, 3 * math.pi / 4)
