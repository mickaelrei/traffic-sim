from typing import Callable
import pygame
import utils
import math
import json
from pygame.event import Event
from pygame.math import Vector2
from model.app import PygameApp
from model.road import Road, RoadLine, StraightRoad, Roundabout, topRightCurvedRoad, topLeftCurvedRoad, bottomRightCurvedRoad, bottomLeftCurvedRoad
from random import randint

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

# Defines the callback for all rules in a 1x2 grid
def rule1x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    tileSize: float,
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

            return ruleStraightHorizontalRoad(topLeft, tileSize, nodesGraph, leftOffset, rightOffset)
        case 1:
            tileMap[y + 1][x] = TILE_STRAIGHT_ROAD

            # Check if tiles to left/right are curves
            leftOffset = 0
            if x > 0 and tileMap[y + 1][x - 1] == TILE_CURVED_ROAD:
                leftOffset = curveArcOffset
            rightOffset = 0
            if x < mapSize.x - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                rightOffset = -curveArcOffset

            return ruleStraightHorizontalRoad(topLeft + Vector2(0, 1), tileSize, nodesGraph, leftOffset, rightOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x1 grid
def rule2x1(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    tileSize: float,
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

            return ruleStraightVerticalRoad(topLeft, tileSize, nodesGraph, topOffset, bottomOffset)
        case 1:
            tileMap[y][x + 1] = TILE_STRAIGHT_ROAD

            # Check if tiles on top/bottom are curves
            topOffset = 0
            if y > 0 and tileMap[y - 1][x + 1] == TILE_CURVED_ROAD:
                topOffset = curveArcOffset
            bottomOffset = 0
            if y < mapSize.y - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                bottomOffset = -curveArcOffset

            return ruleStraightVerticalRoad(topLeft + Vector2(1, 0), tileSize, nodesGraph, topOffset, bottomOffset)
        
    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x2 grid
def rule2x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    tileSize: float,
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
            return ruleTopRightCorner(topLeft, tileSize, nodesGraph, curveArcOffset)
        case 1101:
            tileMap[y][x + 1] = TILE_CURVED_ROAD
            return ruleTopLeftCorner(topLeft, tileSize, nodesGraph, curveArcOffset)
        case 1011:
            tileMap[y + 1][x] = TILE_CURVED_ROAD
            return ruleBottomRightCorner(topLeft, tileSize, nodesGraph, curveArcOffset)
        case 111:
            tileMap[y + 1][x + 1] = TILE_CURVED_ROAD
            return ruleBottomLeftCorner(topLeft, tileSize, nodesGraph, curveArcOffset)
        
    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 5x5 grid
def rule5x5(
    topLeft: Vector2,
    tileMap: list[list[int]],
    nodesGraph: dict[str, list[Vector2]],
    mapSize: Vector2,
    tileSize: float,
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
            return rule4pointIntersection(topLeft, tileSize, nodesGraph, curveArcOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for when the rule for a straight horizontal road is met
def ruleStraightHorizontalRoad(
    topLeft: Vector2,
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    leftOffset: float = 0,
    rightOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight horizontal road
    start = (topLeft - Vector2(0.5, 0)) * tileSize + Vector2(leftOffset, 0)
    end = (topLeft + Vector2(0.5, 0)) * tileSize + Vector2(rightOffset, 0)
    roads.append(StraightRoad(tileSize, start, end))

    # Points to be added
    points: list[Vector2] = [
        start + Vector2(0, tileSize / 4),
        start + Vector2(0, -tileSize / 4),
        end + Vector2(0, tileSize / 4),
        end + Vector2(0, -tileSize / 4),
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
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    topOffset: float = 0,
    bottomOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight vertical road
    start = (topLeft - Vector2(0, 0.5)) * tileSize + Vector2(0, topOffset)
    end = (topLeft + Vector2(0, 0.5)) * tileSize + Vector2(0, bottomOffset)
    roads.append(StraightRoad(tileSize, start, end))

    # Points to be added
    points: list[Vector2] = [
        start + Vector2(tileSize / 4, 0),
        start + Vector2(-tileSize / 4, 0),
        end + Vector2(tileSize / 4, 0),
        end + Vector2(-tileSize / 4, 0),
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
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top right curve
    roads.append(topRightCurvedRoad(tileSize, topLeft * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        topLeft * tileSize + Vector2(-tileSize / 4, tileSize / 2 + curveArcOffset),
        topLeft * tileSize + Vector2(tileSize / 4, tileSize / 2 + curveArcOffset),
        topLeft * tileSize + Vector2(tileSize / 2 + curveArcOffset, tileSize / 4),
        topLeft * tileSize + Vector2(tileSize / 2 + curveArcOffset, -tileSize / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[1])] = [points[2]]
    nodesGraph[utils.vecToStr(points[3])] = [points[0]]


    return roads, points

# Defines the callback for when the rule for a top left corner is met
def ruleTopLeftCorner(
    topLeft: Vector2,
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top left curve
    roadCenter = topLeft + Vector2(1, 0)
    roads.append(topLeftCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * tileSize + Vector2(-tileSize / 4, tileSize / 2 + curveArcOffset),
        roadCenter * tileSize + Vector2(tileSize / 4, tileSize / 2 + curveArcOffset),
        roadCenter * tileSize + Vector2(-tileSize / 2 - curveArcOffset, tileSize / 4),
        roadCenter * tileSize + Vector2(-tileSize / 2 - curveArcOffset, -tileSize / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[1])] = [points[3]]
    nodesGraph[utils.vecToStr(points[2])] = [points[0]]

    return roads, points

# Defines the callback for when the rule for a bottom right corner is met
def ruleBottomRightCorner(
    topLeft: Vector2,
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom right curve
    roadCenter = topLeft + Vector2(0, 1)
    roads.append(bottomRightCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * tileSize + Vector2(-tileSize / 4, -tileSize / 2 - curveArcOffset),
        roadCenter * tileSize + Vector2(tileSize / 4, -tileSize / 2 - curveArcOffset),
        roadCenter * tileSize + Vector2(tileSize / 2 + curveArcOffset, tileSize / 4),
        roadCenter * tileSize + Vector2(tileSize / 2 + curveArcOffset, -tileSize / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[3])] = [points[1]]
    nodesGraph[utils.vecToStr(points[0])] = [points[2]]

    return roads, points

# Defines the callback for when the rule for a bottom left corner is met
def ruleBottomLeftCorner(
    topLeft: Vector2,
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roadCenter = topLeft + Vector2(1, 1)
    roads.append(bottomLeftCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = [
        roadCenter * tileSize + Vector2(-tileSize / 4, -tileSize / 2 - curveArcOffset),
        roadCenter * tileSize + Vector2(tileSize / 4, -tileSize / 2 - curveArcOffset),
        roadCenter * tileSize + Vector2(-tileSize / 2 - curveArcOffset, tileSize / 4),
        roadCenter * tileSize + Vector2(-tileSize / 2 - curveArcOffset, -tileSize / 4),
    ]

    # Set graph connections
    nodesGraph[utils.vecToStr(points[2])] = [points[1]]
    nodesGraph[utils.vecToStr(points[0])] = [points[3]]

    return roads, points

# Defines the callback for when the rule for a 4-point intersection is met
def rule4pointIntersection(
    topLeft: Vector2,
    tileSize: float,
    nodesGraph: dict[str, list[Vector2]],
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roadCenter = topLeft + Vector2(2, 2)
    roads.append(Roundabout(tileSize, roadCenter * tileSize, True, True, True, True))

    # Add straight roads
    # Left
    leftCenter = roadCenter + Vector2(-2, 0)
    roads.append(StraightRoad(tileSize, (leftCenter - Vector2(0.5, 0)) * tileSize, (leftCenter + Vector2(0.5, 0)) * tileSize))
    # Right
    rightCenter = roadCenter + Vector2(2, 0)
    roads.append(StraightRoad(tileSize, (rightCenter - Vector2(0.5, 0)) * tileSize, (rightCenter + Vector2(0.5, 0)) * tileSize))
    # Top
    topCenter = roadCenter + Vector2(0, -2)
    roads.append(StraightRoad(tileSize, (topCenter - Vector2(0, 0.5)) * tileSize, (topCenter + Vector2(0, 0.5)) * tileSize))
    # Bottom
    bottomCenter = roadCenter + Vector2(0, 2)
    roads.append(StraightRoad(tileSize, (bottomCenter - Vector2(0, 0.5)) * tileSize, (bottomCenter + Vector2(0, 0.5)) * tileSize))

    # Points to be added
    points: list[Vector2] = []

    # Angles (in terms of pi) in which the roundabout will have nodes
    angles = [1.85, 1.65, 1.35, 1.15, 0.85, 0.65, 0.35, 0.15]
    dist = 5 * tileSize / 4
    numSteps = 4
    step = 1 / numSteps
    for i in range(0, len(angles) - 1, 2):
        angle0 = angles[i] * math.pi
        angle1 = angles[i + 1] * math.pi
        for s in range(numSteps):
            t = s * step
            angle = angle0 + (angle1 - angle0) * t
            points.append(roadCenter * tileSize + Vector2(math.cos(angle), math.sin(angle)) * dist)

    # Set graph connections inside roundabout
    pointsInside = len(points)
    for i in range(pointsInside):
        nodesGraph[utils.vecToStr(points[i])] = [points[(i + 1) % len(points)]]

    # Add points on straight roads pointing inside roundabout
    points.append((leftCenter + Vector2(0.5, -0.25)) * tileSize)
    points.append((leftCenter + Vector2(0.5, 0.25)) * tileSize)
    points.append((bottomCenter + Vector2(-0.25, -0.5)) * tileSize)
    points.append((bottomCenter + Vector2(0.25, -0.5)) * tileSize)
    points.append((rightCenter + Vector2(-0.5, 0.25)) * tileSize)
    points.append((rightCenter + Vector2(-0.5, -0.25)) * tileSize)
    points.append((topCenter + Vector2(0.25, 0.5)) * tileSize)
    points.append((topCenter + Vector2(-0.25, 0.5)) * tileSize)

    # Add points on straight roads pointing out
    points.append((leftCenter + Vector2(-0.5, -0.25)) * tileSize)
    points.append((leftCenter + Vector2(-0.5, 0.25)) * tileSize)
    points.append((bottomCenter + Vector2(-0.25, 0.5)) * tileSize)
    points.append((bottomCenter + Vector2(0.25, 0.5)) * tileSize)
    points.append((rightCenter + Vector2(0.5, 0.25)) * tileSize)
    points.append((rightCenter + Vector2(0.5, -0.25)) * tileSize)
    points.append((topCenter + Vector2(0.25, -0.5)) * tileSize)
    points.append((topCenter + Vector2(-0.25, -0.5)) * tileSize)

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
rules: list[tuple[str, Callable]] = [
    ('2|2', rule2x2),
    ('1|2', rule1x2),
    ('2|1', rule2x1),
    ('5|5', rule5x5),
]

# Sort rules
def sortRules(r: tuple[str, Callable]) -> None:
    rsizeX, rsizeY = r[0].split("|")
    rsizeX, rsizeY = int(rsizeX), int(rsizeY)

    return rsizeX**2 + rsizeY**2

rules.sort(key=sortRules, reverse=True)

# App for testing path algorithm and map loading
class ShortPathAlgorithmApp(PygameApp):
    def __init__(self, width: int, height: int, fps: float = 60, roadMapFilePath: str | None = None) -> None:
        super().__init__(width, height, fps)

        self.startNodeIndex: int | None = None
        self.endNodeIndex: int | None = None

        self.leftMouseButtonDown = False
        self.cameraOffset = Vector2(0, 0)

        self.roads: list[Road] = []

        self.points: list[Vector2] = []
        self.nodesGraph: dict[str, list[Vector2]] = {}

        self.path = None
        self.dma = None

        self.loadRoadMap(roadMapFilePath)

    def loadRoadMap(self, filePath: str) -> None:
        roadLines: list[RoadLine] = []
        with open(filePath, "r") as f:
            lst = json.load(f)
            for obj in lst:
                # Multiply all coordinates by 2 to create between-tile spacing
                roadLines.append(RoadLine(
                    Vector2(
                        obj["start"]["x"] * 2,
                        obj["start"]["y"] * 2,
                    ),
                    Vector2(
                        obj["end"]["x"] * 2,
                        obj["end"]["y"] * 2,
                    ),
                ))

        # TODO: What to do after loading road lines from JSON:
        # - Get road full path by traversing through road connections (start to end, or end to start)
        # - Get curve points by checking angle difference between points
        # - Generate points for both left and right ways on each curve's start/end points
        # - Generate points graph to be able to use A* algorithm for path generation
        minX = minY = 1e10
        maxX = maxY = -1e10
        for roadLine in roadLines:
            minX = min(minX, roadLine.start.x, roadLine.end.x)
            minY = min(minY, roadLine.start.y, roadLine.end.y)
            maxX = max(maxX, roadLine.start.x, roadLine.end.x)
            maxY = max(maxY, roadLine.start.y, roadLine.end.y)
        minX = int(minX)
        minY = int(minY)
        maxX = int(maxX)
        maxY = int(maxY)
        sizeX = maxX - minX + 1
        sizeY = maxY - minY  +1
        size = Vector2(sizeX, sizeY)

        # Create tile map filled with zeros and change to 1 on all road tiles
        self.tiles = [[0] * sizeX for _ in range(sizeY)]
        # TODO: Maybe this could be optimized
        for j in range(sizeY):
            for i in range(sizeX):
                p = Vector2(i + minX, j + minY)
                for line in roadLines:
                    if line.contains(p):
                        self.tiles[j][i] = 1

        # Check rules to identify curves and calculate node points
        for rule, callback in rules:
            lines = rule.split("|")
            sx = int(lines[0])
            sy = int(lines[1])

            for y in range(sizeY - sy + 1):
                for x in range(sizeX - sx + 1):
                    # Get new possible roads and points
                    roads, points = callback(Vector2(x, y), self.tiles, self.nodesGraph, size, 110, 45)
                    self.roads.extend(roads)
                    self.points.extend(points)

    def generateLinearGraph(self, points: list[Vector2]) -> None:
        if len(self.points) == 0:
            return

        # Set neighbors for each node
        for i in range(len(points) - 1):
            self.nodesGraph[utils.vecToStr(points[i])] = [points[i + 1]]

        # Neighbors for last node
        self.nodesGraph[utils.vecToStr(points[-1])] = [points[0]]

    def newPath(self) -> None:
        if len(self.points) == 0:
            self.startNodeIndex = None
            self.endNodeIndex = None
            return

        start = randint(0, len(self.points) - 1)
        while start == self.startNodeIndex:
            start = randint(0, len(self.points) - 1)
        self.startNodeIndex = start

        end = randint(0, len(self.points) - 1)
        while end == self.endNodeIndex or end == self.startNodeIndex:
            end = randint(0, len(self.points) - 1)
        self.endNodeIndex = end

        startPoint = self.points[self.startNodeIndex]
        endPoint = self.points[self.endNodeIndex]
        self.path = utils.A_Star(self.nodesGraph, startPoint, endPoint)

    def onEvent(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_e:
                self.path = None
                self.dma = None
                while self.path == None:
                    self.newPath()
                print("\n\nnew path")
                self.dma = utils.smoothPathCurves(self.path)
            # Check for mouse motion
        elif event.type == pygame.MOUSEMOTION and self.leftMouseButtonDown:
            self.cameraOffset += Vector2(event.rel)

    def onUpdate(self, dt: float) -> None:
        left, middle, right = pygame.mouse.get_pressed(3)
        self.leftMouseButtonDown = left

        self.window.fill((0, 0, 0))

        for road in self.roads:
            road.draw(self.window, offset=self.cameraOffset, debug=True)

        for point in self.points:
            pygame.draw.circle(self.window, (0, 127, 255), point + self.cameraOffset, 5, 2)

        for node, connections in self.nodesGraph.items():
            x, y = node.split("|")
            start = Vector2(int(x), int(y))
            for p in connections:
                utils.drawArrow(self.window, start + self.cameraOffset, p + self.cameraOffset, (255, 0, 127), 2)

        if self.path != None:
            pygame.draw.circle(self.window, (0, 255, 0), self.points[self.startNodeIndex] + self.cameraOffset, 25)
            pygame.draw.circle(self.window, (0, 255, 0), self.points[self.endNodeIndex] + self.cameraOffset, 25)
            for i in range(len(self.path) - 1):
                p0 = self.path[i]
                utils.drawText(self.window, f"{i}", p0 + Vector2(25) + self.cameraOffset, fontSize=18)
                p1 = self.path[i + 1]

                utils.drawArrow(self.window, p0 + self.cameraOffset, p1 + self.cameraOffset, width=2)
            utils.drawText(self.window, f"{len(self.path) - 1}", self.path[-1] + Vector2(25) + self.cameraOffset, fontSize=18)
            

            for pos in self.dma:
                pygame.draw.circle(self.window, (255, 127, 0), pos + self.cameraOffset, 5)
