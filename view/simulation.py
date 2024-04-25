from model.app import PygameApp
from model.traffic_sim import TrafficSim
from model.road import Road, StraightRoad, RoadLine, topLeftCurvedRoad, topRightCurvedRoad, bottomLeftCurvedRoad, bottomRightCurvedRoad
from model.path import Path
from model.car import Car
from model.driver import Driver
import utils
import math
import pygame
import json
from pygame.event import Event
from pygame.math import Vector2

BLACK = (0, 0, 0)

# Hardcoded tiled map
tileMap = [
    ['  ', '  ', '  ', '  ', 'tr', 'sh', 'sh', 'tl', '  ', '  ', '  ', '  ', '  '],
    ['  ', '  ', '  ', '  ', 'sv', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['  ', '  ', '  ', '  ', 'sv', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['  ', '  ', '  ', '  ', 'sv', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['tr', 'sh', 'sh', 'sh', 'bl', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['sv', '  ', '  ', '  ', '  ', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['sv', '  ', '  ', '  ', '  ', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['br', 'sh', 'sh', 'sh', 'sh', 'tl', '  ', 'sv', '  ', '  ', '  ', '  ', '  '],
    ['  ', '  ', '  ', '  ', '  ', 'sv', '  ', 'br', 'sh', 'sh', 'sh', 'sh', 'tl'],
    ['  ', '  ', '  ', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  ', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  ', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', 'sv', '  ', '  ', '  ', '  ', '  ', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', 'br', 'sh', 'sh', 'sh', 'sh', 'tl', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', 'sv', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', 'sv', '  ', 'sv'],
    ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', 'br', 'sh', 'bl'],
]

# Tile size
tileSize = 110

# Curve arc offset
curveArcOffset = 45

# Create hardcoded path for driver
path = Path([
    Vector2(
        3.5 * tileSize - curveArcOffset,
        3.75 * tileSize,
    ),
    Vector2(
        0.5 * tileSize + curveArcOffset,
        3.75 * tileSize
    ),
    Vector2(
        -0.25 * tileSize,
        4.5 * tileSize + curveArcOffset
    ),
    Vector2(
        -0.25 * tileSize,
        6.5 * tileSize - curveArcOffset
    ),
    Vector2(
        0.5 * tileSize + curveArcOffset,
        7.25 * tileSize
    ),
    Vector2(
        4.5 * tileSize - curveArcOffset,
        7.25 * tileSize
    ),
    Vector2(
        4.75 * tileSize,
        7.5 * tileSize + curveArcOffset
    ),
    Vector2(
        4.75 * tileSize,
        11.5 * tileSize - curveArcOffset
    ),
    Vector2(
        5.5 * tileSize + curveArcOffset,
        12.25 * tileSize,
    ),
    Vector2(
        9.5 * tileSize - curveArcOffset,
        12.25 * tileSize,
    ),
    Vector2(
        9.75 * tileSize,
        12.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        9.75 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        10.5 * tileSize + curveArcOffset,
        15.25 * tileSize,
    ),
    Vector2(
        11.5 * tileSize - curveArcOffset,
        15.25 * tileSize,
    ),
    Vector2(
        12.25 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        12.25 * tileSize,
        8.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        11.5 * tileSize - curveArcOffset,
        7.75 * tileSize,
    ),
    Vector2(
        7.5 * tileSize + curveArcOffset,
        7.75 * tileSize,
    ),
    Vector2(
        7.25 * tileSize,
        7.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        7.25 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        6.5 * tileSize - curveArcOffset,
        -0.25 * tileSize,
    ),
    Vector2(
        4.5 * tileSize + curveArcOffset,
        -0.25 * tileSize,
    ),
    Vector2(
        3.75 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        3.75 * tileSize,
        3.5 * tileSize - curveArcOffset,
    ),
])


# Make path smoother on curves
path = utils.smoothPathCurves(path)

# Other way path
path1 = Path([
    Vector2(
        3.5 * tileSize - curveArcOffset,
        4.25 * tileSize,
    ),
    Vector2(
        0.5 * tileSize + curveArcOffset,
        4.25 * tileSize
    ),
    Vector2(
        0.25 * tileSize,
        4.5 * tileSize + curveArcOffset
    ),
    Vector2(
        0.25 * tileSize,
        6.5 * tileSize - curveArcOffset
    ),
    Vector2(
        0.5 * tileSize + curveArcOffset,
        6.75 * tileSize
    ),
    Vector2(
        4.5 * tileSize - curveArcOffset,
        6.75 * tileSize
    ),
    Vector2(
        5.25 * tileSize,
        7.5 * tileSize + curveArcOffset
    ),
    Vector2(
        5.25 * tileSize,
        11.5 * tileSize - curveArcOffset
    ),
    Vector2(
        5.5 * tileSize + curveArcOffset,
        11.75 * tileSize,
    ),
    Vector2(
        9.5 * tileSize - curveArcOffset,
        11.75 * tileSize,
    ),
    Vector2(
        10.25 * tileSize,
        12.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        10.25 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        10.5 * tileSize + curveArcOffset,
        14.75 * tileSize,
    ),
    Vector2(
        11.5 * tileSize - curveArcOffset,
        14.75 * tileSize,
    ),
    Vector2(
        11.75 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        11.75 * tileSize,
        8.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        11.5 * tileSize - curveArcOffset,
        8.25 * tileSize,
    ),
    Vector2(
        7.5 * tileSize + curveArcOffset,
        8.25 * tileSize,
    ),
    Vector2(
        6.75 * tileSize,
        7.5 * tileSize - curveArcOffset,
    ),
    Vector2(
        6.75 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        6.5 * tileSize - curveArcOffset,
        0.25 * tileSize,
    ),
    Vector2(
        4.5 * tileSize + curveArcOffset,
        0.25 * tileSize,
    ),
    Vector2(
        4.25 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ),
    Vector2(
        4.25 * tileSize,
        3.5 * tileSize - curveArcOffset,
    ),
])

path1 = utils.smoothPathCurves(path1)
path1.nodes.reverse()

# Create car instance positioned at first path node
car = Car(
    path.nodes[0].copy(),
    size=22,
    texturePath="img/car.png",
    textureScale=3.0,
    textureOffsetAngle=180,
    wheelAxisAspectRatio=1.8,
    initialRotation=math.pi
)

car2 = Car(
    path.nodes[1].copy(),
    size=22,
    texturePath="img/car.png",
    textureScale=3.0,
    textureOffsetAngle=180,
    wheelAxisAspectRatio=1.8,
    initialRotation=math.pi
)

# Create driver instance
driver = Driver(
    car=car,
    path=path,
    desiredVelocity=110,
)

driver2 = Driver(
    car=car2,
    path=path,
    initialPathNodeIndex=1
)

# Car for second path
car1 = Car(
    path1.nodes[0].copy(),
    size=22,
    texturePath="img/car.png",
    textureScale=3.0,
    textureOffsetAngle=180,
    wheelAxisAspectRatio=1.8,
    initialRotation=0
)

# Create driver instance
driver1 = Driver(
    car=car1,
    path=path1
)

# Pygame app to show a traffic simulation


class TrafficSimulationApp(PygameApp):
    def __init__(self, width: int, height: int, fps: float = 60, roadMapFilePath: str | None = None) -> None:
        super().__init__(width, height, fps)

        # Whether debug rendering is on
        self.debug = False

        # Whether simulation is updating (useful for pausing)
        self.update = True

        # Whether fast update is on (useful for speeding up simulation)
        self.fastUpdate = False

        # Whether a driver is currently focused
        self.isFocused = False

        # Rendering offset, serving as camera position
        self.cameraOffset = Vector2(0, 0)

        # Rendering rotation, serving as camera rotation
        self.cameraRotation = 0

        # Camera rotation direction (0 is not rotating, -1 is left and 1 is right)
        self.cameraRotateDirection = 0

        # How fast the camera rotates
        self.cameraRotateSpeed = 1

        # Currently focused driver
        self.focusedIndex = 0

        # Whether mouse left button is down
        self.leftMouseButtonDown = False

        # Traffic simulation
        self.trafficSim = TrafficSim()
        self.trafficSim.addDriver(driver)
        self.trafficSim.addDriver(driver1)
        self.trafficSim.addDriver(driver2)

        self.roads: list[Road] = []
        for j, line in enumerate(tileMap):
            for i, code in enumerate(line):
                # Get center
                center = Vector2(i * tileSize, j * tileSize)

                if code == 'tr':
                    self.roads.append(topRightCurvedRoad(
                        tileSize,
                        center,
                        curveArcOffset,
                    ))
                elif code == 'tl':
                    self.roads.append(topLeftCurvedRoad(
                        tileSize,
                        center,
                        curveArcOffset,
                    ))
                elif code == 'br':
                    self.roads.append(bottomRightCurvedRoad(
                        tileSize,
                        center,
                        curveArcOffset,
                    ))
                elif code == 'bl':
                    self.roads.append(bottomLeftCurvedRoad(
                        tileSize,
                        center,
                        curveArcOffset,
                    ))
                elif code == 'sv':
                    # Check for curve roads on top and bottom
                    # Top
                    leftDiff = 0
                    if j > 0 and tileMap[j-1][i] in ('tr', 'tl', 'br', 'bl'):
                        leftDiff = -curveArcOffset
                    # Bottom
                    rightDiff = 0
                    if j < len(tileMap) - 1 and tileMap[j+1][i] in ('tr', 'tl', 'br', 'bl'):
                        rightDiff = -curveArcOffset
                    self.roads.append(StraightRoad(
                        tileSize,
                        center - Vector2(0, tileSize/2 + leftDiff),
                        center + Vector2(0, tileSize/2 + rightDiff),
                    ))
                elif code == 'sh':
                    # Check for curve roads on left and right
                    # Left
                    leftDiff = 0
                    if i > 0 and tileMap[j][i-1] in ('tr', 'tl', 'br', 'bl'):
                        leftDiff = -curveArcOffset
                    # Right
                    rightDiff = 0
                    if i < len(tileMap[j]) - 1 and tileMap[j][i+1] in ('tr', 'tl', 'br', 'bl'):
                        rightDiff = -curveArcOffset
                    self.roads.append(StraightRoad(
                        tileSize,
                        center - Vector2(tileSize/2 + leftDiff, 0),
                        center + Vector2(tileSize/2 + rightDiff, 0),
                    ))

        # Load road map
        if roadMapFilePath != None:
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

        tiles = [[0] * sizeX for _ in range(sizeY)]

        # TODO: Maybe this could be optimized
        for j in range(sizeY):
            for i in range(sizeX):
                p = Vector2(i + minX, j + minY)
                for line in roadLines:
                    if line.contains(p):
                        tiles[j][i] = 1

        # TODO: Run loops to identify curves and calculate node points

    def onEvent(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        # Check for key presses
        elif event.type == pygame.KEYDOWN:
            # Debug toggle
            if event.key == pygame.K_f:
                self.debug = not self.debug
            # Toggle updating
            elif event.key == pygame.K_v:
                self.update = not self.update
            # Car focus change
            elif event.key == pygame.K_z and self.isFocused:
                self.focusedIndex = (self.focusedIndex -
                                     1) % len(self.trafficSim.drivers)
            elif event.key == pygame.K_c and self.isFocused:
                self.focusedIndex = (self.focusedIndex +
                                     1) % len(self.trafficSim.drivers)
            elif event.key == pygame.K_x:
                if self.isFocused:
                    # Make camera stay at focused car position and rotation
                    focusedCar = self.trafficSim.drivers[self.focusedIndex].car
                    self.cameraOffset = -focusedCar.pos + \
                        Vector2(self.width, self.height)
                    self.cameraRotation = focusedCar.rotation + math.pi / 2
                self.isFocused = not self.isFocused
            # Camera rotation
            elif event.key == pygame.K_q:
                self.cameraRotateDirection += -1
            elif event.key == pygame.K_e:
                self.cameraRotateDirection += 1
            elif event.key == pygame.K_h:
                self.fastUpdate = not self.fastUpdate
        # Check for key releases
        elif event.type == pygame.KEYUP:
            # Camera rotation
            if event.key == pygame.K_q:
                self.cameraRotateDirection -= -1
            elif event.key == pygame.K_e:
                self.cameraRotateDirection -= 1
        # Check for mouse motion
        elif event.type == pygame.MOUSEMOTION and self.leftMouseButtonDown and not self.isFocused:
            self.cameraOffset += Vector2(event.rel).rotate(
                math.degrees(self.cameraRotation),
            )

    def onUpdate(self, dt: float) -> None:
        # Get mouse buttons state
        left, middle, right = pygame.mouse.get_pressed(3)
        self.leftMouseButtonDown = left

        # Update camera rotation (only if not focused)
        if not self.isFocused:
            self.cameraRotation += self.cameraRotateDirection * self.cameraRotateSpeed * dt

        # Get focused car offset
        if self.isFocused:
            focusedCar = self.trafficSim.drivers[self.focusedIndex].car
            worldOffset = -focusedCar.pos + Vector2(self.width, self.height)
        else:
            worldOffset = self.cameraOffset

        # Clear window
        self.window.fill(BLACK)

        # Traffic drawing surface
        trafficSurface = pygame.Surface((self.width * 2, self.height * 2))

        # NOTE: This is for testing the roundabout; remove when testing is done
        # center = Vector2(self.width/2, self.height/2)
        # r = Roundabout(tileSize, center, connectTop=False, connectLeft=True, connectBottom=True, connectRight=True)
        # r.draw(trafficSurface, worldOffset, self.debug)

        # start = center - Vector2(tileSize * 2, 0)
        # l = StraightRoad(tileSize, start, start + Vector2(-1000, 0))
        # l.draw(trafficSurface, worldOffset, self.debug)

        # start = center + Vector2(tileSize * 2, 0)
        # r = StraightRoad(tileSize, start, start + Vector2(1000, 0))
        # r.draw(trafficSurface, worldOffset, self.debug)

        # start = center - Vector2(0, tileSize * 2)
        # t = StraightRoad(tileSize, start, start + Vector2(0, -1000))
        # t.draw(trafficSurface, worldOffset, self.debug)

        # start = center + Vector2(0, tileSize * 2)
        # b = StraightRoad(tileSize, start, start + Vector2(0, 1000))
        # b.draw(trafficSurface, worldOffset, self.debug)

        # Draw the roads
        for road in self.roads:
            road.draw(trafficSurface, worldOffset, self.debug)

        # Update and draw traffic
        if self.update:
            if self.fastUpdate:
                for _ in range(5):
                    self.trafficSim.update(dt)
            self.trafficSim.update(dt)
        self.trafficSim.draw(trafficSurface, worldOffset, self.debug)

        # Check if any car is focused
        if self.isFocused:
            focusedCar = self.trafficSim.drivers[self.focusedIndex].car

            # Get rotated traffic surface based on focused car
            rotatedTraffic = pygame.transform.rotate(
                trafficSurface,
                math.degrees(focusedCar.rotation + math.pi / 2),
            )
            trafficRect = rotatedTraffic.get_rect(
                center=trafficSurface.get_rect(
                    center=(
                        self.width/2, self.height/2,
                    ),
                ).center,
            )
        else:
            # Get rotated traffic surface based on current camera rotation
            rotatedTraffic = pygame.transform.rotate(
                trafficSurface, math.degrees(self.cameraRotation))
            trafficRect = rotatedTraffic.get_rect(center=trafficSurface.get_rect(
                center=(self.width/2, self.height/2)).center)

        # Draw rotated traffic surface on window
        self.window.blit(rotatedTraffic, trafficRect)

        # Draw text indicating which car is focused
        utils.drawText(
            surface=self.window,
            text=f'Focused car: {self.focusedIndex if self.isFocused else "None"}',
            pos=Vector2(5, self.height - 5),
            anchorX=0.5,
            anchorY=-0.5,
            fontSize=25,
        )
