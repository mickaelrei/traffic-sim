import pygame
import math
import utils
from pygame.math import Vector2

# Color of road outlines
ROAD_OUTLINE_COLOR = (140, 140, 140)

# Color of road middle yellow stripes
ROAD_YELLOW_STRIPE_COLOR = (140, 140, 0)

# How thick are the road outlines
ROAD_OUTLINE_WIDTH = 3


# Class to help with visualizing a roadmap's line
class RoadLine:
    def __init__(self, start: Vector2, end: Vector2) -> None:
        self.start = start
        self.end = end

    # Returns whether a given [point] lies on this road line
    def contains(self, point: Vector2) -> bool:
        liesInX = (
            min(self.start.x, self.end.x) <= point.x <= max(self.start.x, self.end.x)
        )
        liesInY = (
            min(self.start.y, self.end.y) <= point.y <= max(self.start.y, self.end.y)
        )
        slopeY = (self.end.x - self.start.x) * (point.y - self.start.y)
        slopeX = (self.end.y - self.start.y) * (point.x - self.start.x)

        return liesInX and liesInY and abs(slopeY - slopeX) < 1e5

    def __repr__(self) -> str:
        return f"[{self.start.x:.0f}, {self.start.y:.0f}] - [{self.end.x:.0f}, {self.end.y:.0f}]"

    def toJSON(self) -> dict:
        return {
            "start": {
                "x": self.start.x,
                "y": self.start.y,
            },
            "end": {
                "x": self.end.x,
                "y": self.end.y,
            },
        }


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
        curveArcOffset: float = 0,
    ) -> None:
        super().__init__(width)
        self.center = center
        self.connectBottom = connectBottom
        self.connectTop = connectTop
        self.connectLeft = connectLeft
        self.connectRight = connectRight

        # How much bigger is the roundabout
        self.sizeMult = 1.5

    def draw(
        self,
        surface: pygame.Surface,
        offset: Vector2 = Vector2(0, 0),
        debug: bool = False,
    ) -> None:
        # Roundabout outwards arc offset
        arcOffset = self.width / 10

        size = Vector2(self.width * self.sizeMult)

        # Quarter arc angle offset based on road width, to adjust connection to other roads
        offsetAngle = math.asin((self.width / 2 + arcOffset) / (self.width * self.sizeMult))

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
                + utils.directionVector(startAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(endAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(startAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(endAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(startAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(endAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(startAngle) * self.width * self.sizeMult,
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
                + utils.directionVector(endAngle) * self.width * self.sizeMult,
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
            self.width * (self.sizeMult - 1 / 2),
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
