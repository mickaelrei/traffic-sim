import pygame
import utils
import math
from pygame.event import Event
from pygame.math import Vector2
from model.app import PygameApp
from random import randint

BLACK = (0, 0, 0)


class ShortPathAlgorithmApp(PygameApp):
    def __init__(self, width: int, height: int, fps: float = 60) -> None:
        super().__init__(width, height, fps)

        self.startNodeIndex: int | None = None
        self.endNodeIndex: int | None = None

        self.points: list[Vector2] = []
        self.graph: dict[str, list[Vector2]] = {}
        self.path = None

        # Hardcoded points
        self.points.append(Vector2(50, 80))
        self.points.append(Vector2(100, 240))
        self.points.append(Vector2(300, 400))
        self.points.append(Vector2(30, 550))
        self.points.append(Vector2(550, 500))
        self.points.append(Vector2(500, 300))
        self.points.append(Vector2(360, 50))
        self.generateLinearGraph(self.points)

        # Generate other-way points
        newPoints = []
        newPoints.append(Vector2(80, 110))
        newPoints.append(Vector2(135, 220))
        newPoints.append(Vector2(345, 395))
        newPoints.append(Vector2(130, 520))
        newPoints.append(Vector2(515, 475))
        newPoints.append(Vector2(455, 315))
        newPoints.append(Vector2(350, 90))

        newPoints.reverse()
        self.generateLinearGraph(newPoints)
        self.points.extend(newPoints)

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

        self.newPath()
        if self.path == None:
            print("Error creating path")

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
