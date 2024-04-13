from model.car import Car
from model.driver import Driver
from model.traffic_sim import TrafficSim
from model.road import Road, StraightRoad, CurvedRoad, Roundabout, topLeftCurvedRoad, topRightCurvedRoad, bottomLeftCurvedRoad, bottomRightCurvedRoad
from model.path import Path
import utils
import pygame
import sys
import math
from pygame.math import Vector2

pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

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

# Create roads from tilemap
tileSize = 110
curveArcOffset = 45
roads: list[Road] = []
for j, line in enumerate(tileMap):
    for i, code in enumerate(line):
        # Get center
        center = Vector2(i * tileSize, j * tileSize)

        if code == 'tr':
            roads.append(topRightCurvedRoad(tileSize, center, curveArcOffset))
        elif code == 'tl':
            roads.append(topLeftCurvedRoad(tileSize, center, curveArcOffset))
        elif code == 'br':
            roads.append(bottomRightCurvedRoad(tileSize, center, curveArcOffset))
        elif code == 'bl':
            roads.append(bottomLeftCurvedRoad(tileSize, center, curveArcOffset))
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
            roads.append(StraightRoad(tileSize, center - Vector2(0, tileSize/2 + leftDiff), center + Vector2(0, tileSize/2 + rightDiff)))
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
            roads.append(StraightRoad(tileSize, center - Vector2(tileSize/2 + leftDiff, 0), center + Vector2(tileSize/2 + rightDiff, 0)))

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

# Create main traffic simulation instance
trafficSim = TrafficSim()

# Add driver to list
trafficSim.addDriver(driver)
trafficSim.addDriver(driver1)
trafficSim.addDriver(driver2)

# States
debug = False
focusedIndex = 0
isFocused = False
update = True
mouseDown = False
fastUpdate = False

# Camera movement
cameraOffset = Vector2(WIDTH/2, HEIGHT/2)
cameraRotation = 0
cameraRotateSpeed = 1
cameraRotateDirection = 0

# Used to calculate dt
getTicksLastFrame = pygame.time.get_ticks()

# Main game loop
while True:
    # Calculate dt
    t = pygame.time.get_ticks()
    dt = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    # Get mouse pos
    mouseX, mouseY = pygame.mouse.get_pos()

    # Check for events
    for event in pygame.event.get():
        # If press ESC or close window, stop program
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        # Check for key presses
        elif event.type == pygame.KEYDOWN:
            # Car movement (only for testing, barely used)
            if event.key == pygame.K_w:
                car.setAccelerationAmount(1)
            elif event.key == pygame.K_s:
                car.setBrakeAmount(1)
            # Car reverse gear toggle
            elif event.key == pygame.K_r:
                car.reverse = not car.reverse
            # Debug toggle
            elif event.key == pygame.K_f:
                debug = not debug
            # Toggle updating
            elif event.key == pygame.K_v:
                update = not update
            # Car focus change
            elif event.key == pygame.K_z and isFocused:
                focusedIndex = (focusedIndex - 1) % len(trafficSim.drivers)
            elif event.key == pygame.K_c and isFocused:
                focusedIndex = (focusedIndex + 1) % len(trafficSim.drivers)
            elif event.key == pygame.K_x:
                if isFocused:
                    # Make camera stay at focused car position and rotation
                    focusedCar = trafficSim.drivers[focusedIndex].car
                    cameraOffset = -focusedCar.pos + Vector2(WIDTH, HEIGHT)
                    cameraRotation = focusedCar.rotation + math.pi / 2
                isFocused = not isFocused
            # Camera rotation
            elif event.key == pygame.K_q:
                cameraRotateDirection += -1
            elif event.key == pygame.K_e:
                cameraRotateDirection += 1
            elif event.key == pygame.K_h:
                fastUpdate = not fastUpdate
        # Check for key releases
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                car.setAccelerationAmount(0)
            elif event.key == pygame.K_s:
                car.setBrakeAmount(0)
            # Camera rotation
            elif event.key == pygame.K_q:
                cameraRotateDirection -= -1
            elif event.key == pygame.K_e:
                cameraRotateDirection -= 1
        # Check for mouse motion
        elif event.type == pygame.MOUSEMOTION and mouseDown and not isFocused:
            cameraOffset += Vector2(event.rel).rotate(math.degrees(cameraRotation))

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)
    mouseDown = left

    # Update camera rotation (only if not focused)
    if not isFocused:
        cameraRotation += cameraRotateDirection * cameraRotateSpeed * dt

    # Get focused car offset
    if isFocused:
        worldOffset = -trafficSim.drivers[focusedIndex].car.pos + Vector2(WIDTH, HEIGHT)
    else:
        worldOffset = cameraOffset

    # Clear window
    window.fill(BLACK)

    # Traffic drawing surface
    trafficSurface = pygame.Surface((WIDTH * 2, HEIGHT * 2))

    # NOTE: This is for testing the roundabout; remove when testing is done
    # center = Vector2(WIDTH/2, HEIGHT/2)
    # r = Roundabout(tileSize, center, connectTop=True, connectLeft=True, connectBottom=True, connectRight=True)
    # r.draw(trafficSurface, worldOffset, debug)

    # l = StraightRoad(tileSize, Vector2(0, center.y), center - Vector2(tileSize * 2, 0))
    # l.draw(trafficSurface, worldOffset, debug)

    # r = StraightRoad(tileSize, Vector2(WIDTH, center.y), center + Vector2(tileSize * 2, 0))
    # r.draw(trafficSurface, worldOffset, debug)

    # t = StraightRoad(tileSize, Vector2(center.x, 0), center - Vector2(0, tileSize * 2))
    # t.draw(trafficSurface, worldOffset, debug)

    # b = StraightRoad(tileSize, Vector2(center.x, HEIGHT), center + Vector2(0, tileSize * 2))
    # b.draw(trafficSurface, worldOffset, debug)

    # Draw the roads
    for road in roads:
        road.draw(trafficSurface, worldOffset, debug)

    # Manually update car steering based on mouse horizontal position (for now)
    car.setSteering(mouseX / WIDTH * 2 - 1)

    # Update and draw traffic
    if update:
        if fastUpdate:
            for i in range(5):
                trafficSim.update(dt)
        trafficSim.update(dt)
    trafficSim.draw(trafficSurface, worldOffset, debug)

    # Check if any car is focused
    if isFocused:
        focusedCar = trafficSim.drivers[focusedIndex].car

        # Get rotated traffic surface based on focused car
        rotatedTraffic = pygame.transform.rotate(trafficSurface, math.degrees(focusedCar.rotation + math.pi / 2))
        surfSize = trafficSurface.get_size()
        trafficRect = rotatedTraffic.get_rect(center = trafficSurface.get_rect(center = (WIDTH/2, HEIGHT/2)).center)
    else:
        # Get rotated traffic surface based on current camera rotation
        rotatedTraffic = pygame.transform.rotate(trafficSurface, math.degrees(cameraRotation))
        surfSize = trafficSurface.get_size()
        trafficRect = rotatedTraffic.get_rect(center = trafficSurface.get_rect(center = (WIDTH/2, HEIGHT/2)).center)

    # Draw rotated traffic surface on window
    window.blit(rotatedTraffic, trafficRect)

    # Draw text indicating which car is focused
    utils.drawText(window, f'Focused car: {focusedIndex if isFocused else "None"}', Vector2(5, HEIGHT - 5), anchorX=0.5, anchorY=-0.5, fontSize=25)

    # Update window
    pygame.display.update()
    clock.tick(FPS)
