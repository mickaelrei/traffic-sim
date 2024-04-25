import pygame
import utils
import math
import json
from pygame.event import Event
from pygame.math import Vector2
from model.app import PygameApp
from model.road import Road, RoadLine, topRightCurvedRoad, topLeftCurvedRoad, bottomRightCurvedRoad, bottomLeftCurvedRoad
from random import randint

BLACK = (0, 0, 0)

# Defines the callback for when the rule for a top right corner is met
def ruleTopRightCorner(
    p: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    print('Found top right corner')
    # Roads to be added
    roads: list[Road] = []

    # Add top right curve
    roads.append(topRightCurvedRoad(tileSize, p * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a top left corner is met
def ruleTopLeftCorner(
    p: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    print('Found top left corner')
    # Roads to be added
    roads: list[Road] = []

    # Add top left curve
    roads.append(topLeftCurvedRoad(tileSize, p * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a bottom right corner is met
def ruleBottomRightCorner(
    p: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    print('Found bottom right corner')
    # Roads to be added
    roads: list[Road] = []

    # Add bottom right curve
    roads.append(bottomRightCurvedRoad(tileSize, p * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

# Defines the callback for when the rule for a bottom left corner is met
def ruleBottomLeftCorner(
    p: Vector2,
    tileSize: float,
    curveArcOffset: float,
) -> tuple[list[Road], list[Vector2]]:
    print('Found bottom left corner')
    # Roads to be added
    roads: list[Road] = []

    # Add bottom left curve
    roads.append(bottomLeftCurvedRoad(tileSize, p * tileSize, curveArcOffset))

    # Points to be added
    points: list[Vector2] = []

    # TODO: Calculate points around curve

    return roads, points

rules = {
    '11\n'
    '10': ruleTopRightCorner,

    '11\n'
    '01': ruleTopLeftCorner,

    '01\n'
    '11': ruleBottomLeftCorner,

    '10\n'
    '11': ruleBottomRightCorner,
}


class ShortPathAlgorithmApp(PygameApp):
    def __init__(self, width: int, height: int, fps: float = 60, roadMapFilePath: str | None = None) -> None:
        super().__init__(width, height, fps)

        self.startNodeIndex: int | None = None
        self.endNodeIndex: int | None = None

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
        print('Size:', sizeX, sizeY)

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

        # TODO: Run loops to identify curves and calculate node points
        for rule, callback in rules.items():
            lines = rule.split("\n")
            sy = len(lines)
            sx = len(lines[0])

            for y in range(sizeY - sy + 1):
                for x in range(sizeX - sx + 1):
                    valid = True
                    for j in range(sy):
                        ruleLine = lines[j]
                        for i in range(sx):
                            ruleTile = ruleLine[i]
                            if str(self.tiles[y + j][x + i]) != ruleTile:
                                valid = False
                                break
                        if not valid:
                            break

                    if valid:
                        # TODO: These are hardcoded values
                        roads, points = callback(Vector2(x, y), 110, 45)
                        print(f'Got a valid one at pos ({x}, {y})')
                        print(roads)
                        print(points)

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

    def onUpdate(self, dt: float) -> None:
        self.window.fill(BLACK)

        if self.startNodeIndex != None and self.endNodeIndex != None:
            utils.drawArrow(
                self.window, self.points[self.startNodeIndex], self.points[self.endNodeIndex], (255, 255, 255))

        for v, neighbors in self.graph.items():
            x, y = v.split("|")
            p = Vector2(int(x), int(y))
            for neighbor in neighbors:
                utils.drawArrow(self.window, p, neighbor, (0, 0, 255))

        for i, point in enumerate(self.points):
            pygame.draw.circle(self.window, (255, 0, 0), point, 18, 2)
            utils.drawText(self.window, f"{i}", point, fontSize=13)

        if self.path != None:
            for i in range(len(self.path) - 1):
                p0 = self.path[i]
                p1 = self.path[i + 1]
                utils.drawArrow(self.window, p0, p1, (255, 0, 127))
