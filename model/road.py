from typing import Callable
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

# Value for an empty tile
TILE_EMPTY = 0

# Value for a tile meant for a road, not storing anything yet
TILE_ROAD = 1

# Value for a tile storing a curved road
TILE_CURVED_ROAD = 2

# Value for a tile storing a straight road
TILE_STRAIGHT_ROAD = 3

# Value for a tile storing a roundabout
TILE_ROUNDABOUT_ROAD = 4

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

# Defines the callback for all rules in a 1x2 grid
def rule1x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    roadWidth: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Possibilities in a 1x2 grid:
    # - Straight horizontal road on top
    #   [1]
    #   [0]
    #
    # - Straight horizontal road on bottom
    #   [0]
    #   [1]


    # Convert data grid to number
    y = int(topLeft.y)
    x = int(topLeft.x)
    dataNumber = tileMap[y][x] * 10 + tileMap[y + 1][x]

    # Check number match
    match dataNumber:
        case 10:
            # Set tilemap value so other rules won't apply to this tile
            tileMap[y][x] = TILE_STRAIGHT_ROAD

            # Check if tiles to left/right are curves
            leftOffset = 0
            if x > 0 and tileMap[y][x - 1] == TILE_CURVED_ROAD:
                leftOffset = curveArcOffset
            rightOffset = 0
            if x < mapSize.x - 1 and tileMap[y][x + 1] == TILE_CURVED_ROAD:
                rightOffset = -curveArcOffset

            return ruleStraightHorizontalRoad(topLeft, roadWidth, nodesGraph, leftOffset, rightOffset)
        case 1:
            tileMap[y + 1][x] = TILE_STRAIGHT_ROAD

            # Check if tiles to left/right are curves
            leftOffset = 0
            if x > 0 and tileMap[y + 1][x - 1] == TILE_CURVED_ROAD:
                leftOffset = curveArcOffset
            rightOffset = 0
            if x < mapSize.x - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                rightOffset = -curveArcOffset

            return ruleStraightHorizontalRoad(topLeft + Vector2(0, 1), roadWidth, nodesGraph, leftOffset, rightOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x1 grid
def rule2x1(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    roadWidth: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Possibilities in a 1x2 grid:
    # - Straight vertical road on left
    #   [10]
    #
    # - Straight vertical road on right
    #   [01]

    # Convert data grid to number
    y = int(topLeft.y)
    x = int(topLeft.x)
    dataNumber = tileMap[y][x] * 10 + tileMap[y][x + 1]

    # Check number match
    match dataNumber:
        case 10:
            # Set tilemap value so other rules won't apply to this tile
            tileMap[y][x] = TILE_STRAIGHT_ROAD

            # Check if tiles on top/bottom are curves
            topOffset = 0
            if y > 0 and tileMap[y - 1][x] == TILE_CURVED_ROAD:
                topOffset = curveArcOffset
            bottomOffset = 0
            if y < mapSize.y - 1 and tileMap[y + 1][x] == TILE_CURVED_ROAD:
                bottomOffset = -curveArcOffset

            return ruleStraightVerticalRoad(topLeft, roadWidth, nodesGraph, topOffset, bottomOffset)
        case 1:
            tileMap[y][x + 1] = TILE_STRAIGHT_ROAD

            # Check if tiles on top/bottom are curves
            topOffset = 0
            if y > 0 and tileMap[y - 1][x + 1] == TILE_CURVED_ROAD:
                topOffset = curveArcOffset
            bottomOffset = 0
            if y < mapSize.y - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                bottomOffset = -curveArcOffset

            return ruleStraightVerticalRoad(topLeft + Vector2(1, 0), roadWidth, nodesGraph, topOffset, bottomOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x2 grid
def rule2x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    roadWidth: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Possibilities in a 2x2 grid:
    # - Top right corner
    #   [11]
    #   [10]
    #
    # - Top left corner
    #   [11]
    #   [01]
    #
    # - Bottom right corner
    #   [10]
    #   [11]
    #
    # - Bottom left corner
    #   [01]
    #   [11]

    # Convert data grid to number
    y = int(topLeft.y)
    x = int(topLeft.x)
    dataNumber = (
        tileMap[y][x] * 1000
        + tileMap[y][x + 1] * 100
        + tileMap[y + 1][x] * 10
        + tileMap[y + 1][x + 1]
    )

    # Check number match
    match dataNumber:
        case 1110:
            # Set tilemap value so other rules won't apply to this tile
            tileMap[y][x] = TILE_CURVED_ROAD
            return ruleTopRightCorner(topLeft, roadWidth, nodesGraph, curveArcOffset)
        case 1101:
            tileMap[y][x + 1] = TILE_CURVED_ROAD
            return ruleTopLeftCorner(topLeft, roadWidth, nodesGraph, curveArcOffset)
        case 1011:
            tileMap[y + 1][x] = TILE_CURVED_ROAD
            return ruleBottomRightCorner(topLeft, roadWidth, nodesGraph, curveArcOffset)
        case 111:
            tileMap[y + 1][x + 1] = TILE_CURVED_ROAD
            return ruleBottomLeftCorner(topLeft, roadWidth, nodesGraph, curveArcOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 5x5 grid
def rule5x5(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    roadWidth: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Possibilities in a 5x5 grid:
    # - 4-point intersection
    #   [00100]
    #   [00100]
    #   [11111]
    #   [00100]
    #   [00100]

    # Convert data grid to string
    y = int(topLeft.y)
    x = int(topLeft.x)
    dataNumber = (
        f"{tileMap[y + 0][x + 0]}"
        f"{tileMap[y + 0][x + 1]}"
        f"{tileMap[y + 0][x + 2]}"
        f"{tileMap[y + 0][x + 3]}"
        f"{tileMap[y + 0][x + 4]}"
        f"{tileMap[y + 1][x + 0]}"
        f"{tileMap[y + 1][x + 1]}"
        f"{tileMap[y + 1][x + 2]}"
        f"{tileMap[y + 1][x + 3]}"
        f"{tileMap[y + 1][x + 4]}"
        f"{tileMap[y + 2][x + 0]}"
        f"{tileMap[y + 2][x + 1]}"
        f"{tileMap[y + 2][x + 2]}"
        f"{tileMap[y + 2][x + 3]}"
        f"{tileMap[y + 2][x + 4]}"
        f"{tileMap[y + 3][x + 0]}"
        f"{tileMap[y + 3][x + 1]}"
        f"{tileMap[y + 3][x + 2]}"
        f"{tileMap[y + 3][x + 3]}"
        f"{tileMap[y + 3][x + 4]}"
        f"{tileMap[y + 4][x + 0]}"
        f"{tileMap[y + 4][x + 1]}"
        f"{tileMap[y + 4][x + 2]}"
        f"{tileMap[y + 4][x + 3]}"
        f"{tileMap[y + 4][x + 4]}"
    )

    # Check number match
    match dataNumber:
        case "0010000100111110010000100":
            # Set tilemap value so other rules won't apply to this tile
            tileMap[y + 0][x + 2] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 1][x + 2] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 2][x + 2] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 3][x + 2] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 4][x + 2] = TILE_ROUNDABOUT_ROAD

            tileMap[y + 2][x + 0] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 2][x + 1] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 2][x + 2] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 2][x + 3] = TILE_ROUNDABOUT_ROAD
            tileMap[y + 2][x + 4] = TILE_ROUNDABOUT_ROAD
            return rule4pointIntersection(topLeft, roadWidth, nodesGraph, curveArcOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for when the rule for a straight horizontal road is met
def ruleStraightHorizontalRoad(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    leftOffset: float = 0,
    rightOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight horizontal road
    start = (topLeft - Vector2(0.5, 0)) * roadWidth + Vector2(leftOffset, 0)
    end = (topLeft + Vector2(0.5, 0)) * roadWidth + Vector2(rightOffset, 0)
    roads.append(StraightRoad(roadWidth, start, end))

    # Points to be added
    points: list[Vector2] = [
        start + Vector2(0, roadWidth / 4),
        start + Vector2(0, -roadWidth / 4),
        end + Vector2(0, roadWidth / 4),
        end + Vector2(0, -roadWidth / 4),
    ]

    # TODO: Remove this if not needed
    # keyPoint0 = utils.vecToStr(points[0])
    # if nodesGraph.get(keyPoint0) == None:
    #     # Create list if not existent
    #     nodesGraph[keyPoint0] = []
    # else:
    #     print('Already existed?!')
    # nodesGraph[keyPoint0].append(points[2])

    # keyPoint3 = utils.vecToStr(points[3])
    # if nodesGraph.get(keyPoint3) == None:
    #     # Create list if not existent
    #     nodesGraph[keyPoint3] = []
    # else:
    #     print('Already existed?!')
    # nodesGraph[keyPoint3].append(points[1])

    # Set graph connections
    nodesGraph[utils.vecToStr(points[0])] = [points[2]]
    nodesGraph[utils.vecToStr(points[3])] = [points[1]]

    return roads, points

# Defines the callback for when the rule for a straight vertical road is met
def ruleStraightVerticalRoad(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    topOffset: float = 0,
    bottomOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight vertical road
    start = (topLeft - Vector2(0, 0.5)) * roadWidth + Vector2(0, topOffset)
    end = (topLeft + Vector2(0, 0.5)) * roadWidth + Vector2(0, bottomOffset)
    roads.append(StraightRoad(roadWidth, start, end))

    # Points to be added
    points: list[Vector2] = [
        start + Vector2(roadWidth / 4, 0),
        start + Vector2(-roadWidth / 4, 0),
        end + Vector2(roadWidth / 4, 0),
        end + Vector2(-roadWidth / 4, 0),
    ]

    # TODO: Remove this if not needed
    # keyPoint2 = utils.vecToStr(points[2])
    # if nodesGraph.get(keyPoint2) == None:
    #     # Create list if not existent
    #     nodesGraph[keyPoint2] = []
    # else:
    #     print('Already existed?!')
    # nodesGraph[keyPoint2].append(points[0])

    # keyPoint1 = utils.vecToStr(points[1])
    # if nodesGraph.get(keyPoint1) == None:
    #     # Create list if not existent
    #     nodesGraph[keyPoint1] = []
    # else:
    #     print('Already existed?!')
    # nodesGraph[keyPoint1].append(points[3])

    # Set graph connections
    nodesGraph[utils.vecToStr(points[2])] = [points[0]]
    nodesGraph[utils.vecToStr(points[1])] = [points[3]]

    return roads, points

# Defines the callback for when the rule for a top right corner is met
def ruleTopRightCorner(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top right curve
    roads.append(topRightCurvedRoad(roadWidth, topLeft * roadWidth, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        topLeft * roadWidth + Vector2(-roadWidth / 4, roadWidth / 2 + curveArcOffset),
        topLeft * roadWidth + Vector2(roadWidth / 4, roadWidth / 2 + curveArcOffset),
        topLeft * roadWidth + Vector2(roadWidth / 2 + curveArcOffset, roadWidth / 4),
        topLeft * roadWidth + Vector2(roadWidth / 2 + curveArcOffset, -roadWidth / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[1])] = [points[2]]
    nodesGraph[utils.vecToStr(points[3])] = [points[0]]


    return roads, points

# Defines the callback for when the rule for a top left corner is met
def ruleTopLeftCorner(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top left curve
    roadCenter = topLeft + Vector2(1, 0)
    roads.append(topLeftCurvedRoad(roadWidth, roadCenter * roadWidth, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * roadWidth + Vector2(-roadWidth / 4, roadWidth / 2 + curveArcOffset),
        roadCenter * roadWidth + Vector2(roadWidth / 4, roadWidth / 2 + curveArcOffset),
        roadCenter * roadWidth + Vector2(-roadWidth / 2 - curveArcOffset, roadWidth / 4),
        roadCenter * roadWidth + Vector2(-roadWidth / 2 - curveArcOffset, -roadWidth / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[1])] = [points[3]]
    nodesGraph[utils.vecToStr(points[2])] = [points[0]]

    return roads, points

# Defines the callback for when the rule for a bottom right corner is met
def ruleBottomRightCorner(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom right curve
    roadCenter = topLeft + Vector2(0, 1)
    roads.append(bottomRightCurvedRoad(roadWidth, roadCenter * roadWidth, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * roadWidth + Vector2(-roadWidth / 4, -roadWidth / 2 - curveArcOffset),
        roadCenter * roadWidth + Vector2(roadWidth / 4, -roadWidth / 2 - curveArcOffset),
        roadCenter * roadWidth + Vector2(roadWidth / 2 + curveArcOffset, roadWidth / 4),
        roadCenter * roadWidth + Vector2(roadWidth / 2 + curveArcOffset, -roadWidth / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[3])] = [points[1]]
    nodesGraph[utils.vecToStr(points[0])] = [points[2]]

    return roads, points

# Defines the callback for when the rule for a bottom left corner is met
def ruleBottomLeftCorner(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roadCenter = topLeft + Vector2(1, 1)
    roads.append(bottomLeftCurvedRoad(roadWidth, roadCenter * roadWidth, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * roadWidth + Vector2(-roadWidth / 4, -roadWidth / 2 - curveArcOffset),
        roadCenter * roadWidth + Vector2(roadWidth / 4, -roadWidth / 2 - curveArcOffset),
        roadCenter * roadWidth + Vector2(-roadWidth / 2 - curveArcOffset, roadWidth / 4),
        roadCenter * roadWidth + Vector2(-roadWidth / 2 - curveArcOffset, -roadWidth / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[2])] = [points[1]]
    nodesGraph[utils.vecToStr(points[0])] = [points[3]]

    return roads, points

# Defines the callback for when the rule for a 4-point intersection is met
def rule4pointIntersection(
    topLeft: Vector2,
    roadWidth: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roadCenter = topLeft + Vector2(2, 2)
    roads.append(Roundabout(roadWidth, roadCenter * roadWidth, True, True, True, True))

    # Add straight roads
    # Left
    leftCenter = roadCenter + Vector2(-2, 0)
    roads.append(StraightRoad(roadWidth, (leftCenter - Vector2(0.5, 0)) * roadWidth, (leftCenter + Vector2(0.5, 0)) * roadWidth))
    # Right
    rightCenter = roadCenter + Vector2(2, 0)
    roads.append(StraightRoad(roadWidth, (rightCenter - Vector2(0.5, 0)) * roadWidth, (rightCenter + Vector2(0.5, 0)) * roadWidth))
    # Top
    topCenter = roadCenter + Vector2(0, -2)
    roads.append(StraightRoad(roadWidth, (topCenter - Vector2(0, 0.5)) * roadWidth, (topCenter + Vector2(0, 0.5)) * roadWidth))
    # Bottom
    bottomCenter = roadCenter + Vector2(0, 2)
    roads.append(StraightRoad(roadWidth, (bottomCenter - Vector2(0, 0.5)) * roadWidth, (bottomCenter + Vector2(0, 0.5)) * roadWidth))

    # Points to be added
    points: list[Vector2] = []

    # Angles (in terms of pi) in which the roundabout will have nodes
    angles = [1.85, 1.65, 1.35, 1.15, 0.85, 0.65, 0.35, 0.15]
    dist = 5 * roadWidth / 4
    numSteps = 4
    step = 1 / numSteps
    for i in range(0, len(angles) - 1, 2):
        angle0 = angles[i] * math.pi
        angle1 = angles[i + 1] * math.pi
        for s in range(numSteps):
            t = s * step
            angle = angle0 + (angle1 - angle0) * t
            points.append(roadCenter * roadWidth + Vector2(math.cos(angle), math.sin(angle)) * dist)

    # Set graph connections inside roundabout
    pointsInside = len(points)
    for i in range(pointsInside):
        nodesGraph[utils.vecToStr(points[i])] = [points[(i + 1) % len(points)]]

    # Add points on straight roads pointing inside roundabout
    points.append((leftCenter + Vector2(0.5, -0.25)) * roadWidth)
    points.append((leftCenter + Vector2(0.5, 0.25)) * roadWidth)
    points.append((bottomCenter + Vector2(-0.25, -0.5)) * roadWidth)
    points.append((bottomCenter + Vector2(0.25, -0.5)) * roadWidth)
    points.append((rightCenter + Vector2(-0.5, 0.25)) * roadWidth)
    points.append((rightCenter + Vector2(-0.5, -0.25)) * roadWidth)
    points.append((topCenter + Vector2(0.25, 0.5)) * roadWidth)
    points.append((topCenter + Vector2(-0.25, 0.5)) * roadWidth)

    # Add points on straight roads pointing out
    points.append((leftCenter + Vector2(-0.5, -0.25)) * roadWidth)
    points.append((leftCenter + Vector2(-0.5, 0.25)) * roadWidth)
    points.append((bottomCenter + Vector2(-0.25, 0.5)) * roadWidth)
    points.append((bottomCenter + Vector2(0.25, 0.5)) * roadWidth)
    points.append((rightCenter + Vector2(0.5, 0.25)) * roadWidth)
    points.append((rightCenter + Vector2(0.5, -0.25)) * roadWidth)
    points.append((topCenter + Vector2(0.25, -0.5)) * roadWidth)
    points.append((topCenter + Vector2(-0.25, -0.5)) * roadWidth)

    # Connections from outside to inside
    nodesGraph[utils.vecToStr(points[pointsInside + 1])] = [points[numSteps * 2]]
    nodesGraph[utils.vecToStr(points[pointsInside + 3])] = [points[numSteps * 3]]
    nodesGraph[utils.vecToStr(points[pointsInside + 5])] = [points[numSteps * 0]]
    nodesGraph[utils.vecToStr(points[pointsInside + 7])] = [points[numSteps * 1]]

    # Connections from inside to outside
    nodesGraph[utils.vecToStr(points[numSteps * 1 - 1])].append(points[pointsInside + 6])
    nodesGraph[utils.vecToStr(points[numSteps * 2 - 1])].append(points[pointsInside + 0])
    nodesGraph[utils.vecToStr(points[numSteps * 3 - 1])].append(points[pointsInside + 2])
    nodesGraph[utils.vecToStr(points[numSteps * 4 - 1])].append(points[pointsInside + 4])

    # Remaining connections on straight roads' (start to end, roundabout to outside)
    nodesGraph[utils.vecToStr(points[pointsInside + 0])] = [points[pointsInside + 8 + 0]]
    nodesGraph[utils.vecToStr(points[pointsInside + 2])] = [points[pointsInside + 8 + 2]]
    nodesGraph[utils.vecToStr(points[pointsInside + 4])] = [points[pointsInside + 8 + 4]]
    nodesGraph[utils.vecToStr(points[pointsInside + 6])] = [points[pointsInside + 8 + 6]]

    nodesGraph[utils.vecToStr(points[pointsInside + 8 + 1])] = [points[pointsInside + 1]]
    nodesGraph[utils.vecToStr(points[pointsInside + 8 + 3])] = [points[pointsInside + 3]]
    nodesGraph[utils.vecToStr(points[pointsInside + 8 + 5])] = [points[pointsInside + 5]]
    nodesGraph[utils.vecToStr(points[pointsInside + 8 + 7])] = [points[pointsInside + 7]]

    return roads, points

# List of rules for creating roads based on a tilemap
roadRules: list[tuple[str, Callable]] = [
    ('2|2', rule2x2),
    ('1|2', rule1x2),
    ('2|1', rule2x1),
    ('5|5', rule5x5),
]

def _sortRules(r: tuple[str, Callable]) -> None:
    rsizeX, rsizeY = r[0].split("|")
    rsizeX, rsizeY = int(rsizeX), int(rsizeY)

    return rsizeX**2 + rsizeY**2

roadRules.sort(key=_sortRules, reverse=True)