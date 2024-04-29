import pygame
import json
import math
import utils
from random import randint
from pygame.math import Vector2
from model.driver import Driver
from model.car import Car
from model.road import Road, RoadLine, roadRules

# Main class for traffic simulation
class TrafficSim:
    def __init__(self, roadWidth: float, curveArcOffset: float, roadMapFilePath: str, numCars: int) -> None:
        # List of drivers currently in simulation
        self.drivers: list[Driver] = []

        # Road width
        self.roadWidth = roadWidth

        # Curve arc offset
        self.curveArcOffset = curveArcOffset

        # List of roads for rendering
        self.roads: list[Road] = []

        # List of road points for generating paths
        self.points: list[Vector2] = []

        # Nodes graph for creating paths with A*
        self.nodesGraph: dict[str, list[Vector2]] = {}

        self.loadRoadMap(roadMapFilePath)

        # Position cars randomly on the map
        for _ in range(numCars):
            # Get random point
            index = randint(0, len(self.points) - 1)
            angle: float | None = None

            # Make sure it is far from other cars
            valid = False
            attemps = 0
            while not valid and attemps < 30:
                valid = True
                attemps += 1
                index = randint(0, len(self.points) - 1)
                for driver in self.drivers:
                    if (driver.car.pos - self.points[index]).magnitude() < self.roadWidth:
                        valid = False
                        break

                # If position not valid, restart
                if not valid:
                    continue

                # Point is far enough from all other cars, calculate orientation
                point = self.points[index]
                connectsTo = self.nodesGraph[utils.vecToStr(point)]
                if connectsTo != None and len(connectsTo) > 0:
                    # This point is connected to at least one other point, use that orientation
                    direction = (connectsTo[0] - point).normalize()
                    angle = utils.angleFromDirection(direction)
                    if angle < 0:
                        angle += 2 * math.pi

                    # Angle needs to be axis-aligned (either 0, pi/2, pi or 3pi/2)
                    if (
                        abs(angle) > 1e-5 and
                        abs(angle - math.pi / 2) > 1e-5 and
                        abs(angle - math.pi) > 1e-5 and
                        abs(angle - 3 * math.pi / 2) > 1e-5
                    ):
                        valid = False

            # If after many attemps still not valid, can't fit any more cars
            if not valid:
                print(f"Can't fit any more cars. Max cars: {len(self.drivers)}")
                break

            # Add new valid car
            self.addDriver(Driver(
                car=Car(
                    point,
                    size=22,
                    texturePath="img/car.png",
                    textureScale=3.0,
                    textureOffsetAngle=180,
                    wheelAxisAspectRatio=1.8,
                    initialRotation=angle,
                ),
                # TODO: This could be given as a config parameter
                desiredVelocity=randint(70, 110),
            ))

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
                    roads, points = callback(Vector2(x, y), self.tiles, self.nodesGraph, size, self.roadWidth, self.curveArcOffset)
                    self.roads.extend(roads)
                    self.points.extend(points)

    def update(self, dt: float) -> None:
        for driver in self.drivers:
            driver.update(dt, self.drivers, self.points, self.nodesGraph)

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        for driver in self.drivers:
            driver.draw(surface, offset, debug)

    def addDriver(self, driver: Driver) -> None:
        self.drivers.append(driver)
