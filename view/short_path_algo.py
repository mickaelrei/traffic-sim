import pygame
import utils
import math
import json
from pygame.event import Event
from pygame.math import Vector2
from model.app import PygameApp
from model.road import Road, RoadLine, StraightRoad, topRightCurvedRoad, topLeftCurvedRoad, bottomRightCurvedRoad, bottomLeftCurvedRoad
from random import randint

# Value for an empty tile
TILE_EMPTY = 0

# Value for a tile meant for a road, not storing anything yet
TILE_ROAD = 1

# Value for a tile storing a straight road
TILE_STRAIGHT_ROAD = 3

# Value for a tile storing a curved road
TILE_CURVED_ROAD = 2

# Defines the callback for all rules in a 1x2 grid
def rule1x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
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

            return ruleStraightHorizontalRoad(topLeft, tileSize, leftOffset, rightOffset)
        case 1:
            tileMap[y + 1][x] = TILE_STRAIGHT_ROAD

            # Check if tiles to left/right are curves
            leftOffset = 0
            if x > 0 and tileMap[y + 1][x - 1] == TILE_CURVED_ROAD:
                leftOffset = curveArcOffset
            rightOffset = 0
            if x < mapSize.x - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                rightOffset = -curveArcOffset

            return ruleStraightHorizontalRoad(topLeft + Vector2(0, 1), tileSize, leftOffset, rightOffset)

    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x1 grid
def rule2x1(
    topLeft: Vector2,
    tileMap: list[list[int]],
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

            return ruleStraightVerticalRoad(topLeft, tileSize, topOffset, bottomOffset)
        case 1:
            tileMap[y][x + 1] = TILE_STRAIGHT_ROAD

            # Check if tiles on top/bottom are curves
            topOffset = 0
            if y > 0 and tileMap[y - 1][x + 1] == TILE_CURVED_ROAD:
                topOffset = curveArcOffset
            bottomOffset = 0
            if y < mapSize.y - 1 and tileMap[y + 1][x + 1] == TILE_CURVED_ROAD:
                bottomOffset = -curveArcOffset

            return ruleStraightVerticalRoad(topLeft + Vector2(1, 0), tileSize, topOffset, bottomOffset)
        
    # If no matches, return empty lists
    return [], []

# Defines the callback for all rules in a 2x2 grid
def rule2x2(
    topLeft: Vector2,
    tileMap: list[list[int]],
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
            return ruleTopRightCorner(topLeft, tileSize, curveArcOffset)
        case 1101:
            tileMap[y][x + 1] = TILE_CURVED_ROAD
            return ruleTopLeftCorner(topLeft, tileSize, curveArcOffset)
        case 1011:
            tileMap[y + 1][x] = TILE_CURVED_ROAD
            return ruleBottomRightCorner(topLeft, tileSize, curveArcOffset)
        case 111:
            tileMap[y + 1][x + 1] = TILE_CURVED_ROAD
            return ruleBottomLeftCorner(topLeft, tileSize, curveArcOffset)
        
    # If no matches, return empty lists
    return [], []

def ruleStraightHorizontalRoad(
    topLeft: Vector2,
    tileSize: float,
    leftOffset: float = 0,
    rightOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight horizontal road
    roads.append(StraightRoad(
        tileSize,
        (topLeft - Vector2(0.5, 0)) * tileSize + Vector2(leftOffset, 0),
        (topLeft + Vector2(0.5, 0)) * tileSize + Vector2(rightOffset, 0),
    ))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points (if any)

    return roads, points

def ruleStraightVerticalRoad(
    topLeft: Vector2,
    tileSize: float,
    topOffset: float = 0,
    bottomOffset: float = 0,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add straight vertical road
    roads.append(StraightRoad(
        tileSize,
        (topLeft - Vector2(0, 0.5)) * tileSize + Vector2(0, topOffset),
        (topLeft + Vector2(0, 0.5)) * tileSize + Vector2(0, bottomOffset),
    ))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points (if any)

    return roads, points

# Defines the callback for when the rule for a top right corner is met
def ruleTopRightCorner(
    topLeft: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top right curve
    roads.append(topRightCurvedRoad(tileSize, topLeft * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a top left corner is met
def ruleTopLeftCorner(
    topLeft: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add top left curve
    roadCenter = topLeft + Vector2(1, 0)
    roads.append(topLeftCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a bottom right corner is met
def ruleBottomRightCorner(
    topLeft: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom right curve
    roadCenter = topLeft + Vector2(0, 1)
    roads.append(bottomRightCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a bottom left corner is met
def ruleBottomLeftCorner(
    topLeft: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roadCenter = topLeft + Vector2(1, 1)
    roads.append(bottomLeftCurvedRoad(tileSize, roadCenter * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# List of rules for creating roads based on a tilemap
rules = {
    '2|2': rule2x2,
    '1|2': rule1x2,
    '2|1': rule2x1,
}

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
        self.graph: dict[str, list[Vector2]] = {}
        self.path = None

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

        self.tiles = [[0] * sizeX for _ in range(sizeY)]

        # TODO: Maybe this could be optimized
        for j in range(sizeY):
            for i in range(sizeX):
                p = Vector2(i + minX, j + minY)
                for line in roadLines:
                    if line.contains(p):
                        self.tiles[j][i] = 1

        for line in self.tiles:
            for tile in line:
                print(("█" if tile == 1 else ' ') * 2, end='')
            print()

        # Check rules to identify curves and calculate node points
        for rule, callback in rules.items():
            print(f"Applying rule {rule}")
            lines = rule.split("|")
            sx = int(lines[0])
            sy = int(lines[1])

            for y in range(sizeY - sy + 1):
                for x in range(sizeX - sx + 1):
                    # Get new possible roads and points
                    roads, points = callback(Vector2(x, y), self.tiles, size, 110, 45)
                    self.roads.extend(roads)
                    self.points.extend(points)

        for line in self.tiles:
            for tile in line:
                print(str(tile) + " ", end='')
            print()

    def generateLinearGraph(self, points: list[Vector2]) -> None:
        if len(self.points) == 0:
            return

        # Set neighbors for each node
        for i in range(len(points) - 1):
            self.graph[utils.vecToStr(points[i])] = [points[i + 1]]

        # Neighbors for last node
        self.graph[utils.vecToStr(points[-1])] = [points[0]]

    def newPath(self) -> None:
        if len(self.points) == 0:
            self.startNodeIndex = None
            self.endNodeIndex = None
            return

        start = randint(0, len(self.points) - 1)
        while start == self.startNodeIndex:
            start = randint(0, len(self.points) - 1)
        self.startNodeIndex = start

        if start >= 7:
            _min = 7
            _max = len(self.points) - 1
        else:
            _min = 0
            _max = 6

        end = randint(_min, _max)
        while end == self.endNodeIndex or end == self.startNodeIndex:
            end = randint(_min, _max)
        self.endNodeIndex = end

        startPoint = self.points[self.startNodeIndex]
        endPoint = self.points[self.endNodeIndex]
        self.path = utils.A_Star(self.graph, startPoint, endPoint)

    def onEvent(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_e:
                self.newPath()
            # Check for mouse motion
        elif event.type == pygame.MOUSEMOTION and self.leftMouseButtonDown:
            self.cameraOffset += Vector2(event.rel)

    def onUpdate(self, dt: float) -> None:
        left, middle, right = pygame.mouse.get_pressed(3)
        self.leftMouseButtonDown = left

        self.window.fill((0, 0, 0))

        for road in self.roads:
            road.draw(self.window, offset=self.cameraOffset)

        for point in self.points:
            pygame.draw.circle(self.window, (255, 127, 0), point + self.cameraOffset, 15)

        # if self.startNodeIndex != None and self.endNodeIndex != None:
        #     utils.drawArrow(
        #         self.window, self.points[self.startNodeIndex], self.points[self.endNodeIndex], (255, 255, 255))

        # for v, neighbors in self.graph.items():
        #     x, y = v.split("|")
        #     p = Vector2(int(x), int(y))
        #     for neighbor in neighbors:
        #         utils.drawArrow(self.window, p, neighbor, (0, 0, 255))

        # for i, point in enumerate(self.points):
        #     pygame.draw.circle(self.window, (255, 0, 0), point, 18, 2)
        #     utils.drawText(self.window, f"{i}", point, fontSize=13)

        # if self.path != None:
        #     for i in range(len(self.path) - 1):
        #         p0 = self.path[i]
        #         p1 = self.path[i + 1]
        #         utils.drawArrow(self.window, p0, p1, (255, 0, 127))
