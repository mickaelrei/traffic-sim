from typing import Callable
import pygame
import utils
import math
import json
from pygame.event import Event
from pygame.math import Vector2
from model.app import PygameApp
from model.road import Road, RoadLine, roadRules
from random import randint

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
        for rule, callback in roadRules:
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
