from model.car import Car
from model.driver import Driver
from model.traffic_sim import TrafficSim
from model.road import Road, StraightRoad, CurvedRoad, topLeftCurvedRoad, topRightCurvedRoad, bottomLeftCurvedRoad, bottomRightCurvedRoad
from model.path import Path, PathNode
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
curveArcOffset = 35
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

# TODO: Add intermediate path nodes between curves for smoother movement

# Create hardcoded path for driver
path = Path([
    PathNode(Vector2(
        3.5 * tileSize - curveArcOffset,
        3.75 * tileSize,
    ), math.pi),
    PathNode(Vector2(
        0.5 * tileSize + curveArcOffset,
        3.75 * tileSize
    ), math.pi),
    PathNode(Vector2(
        -0.25 * tileSize,
        4.5 * tileSize + curveArcOffset
    ), math.pi / 2),
    PathNode(Vector2(
        -0.25 * tileSize,
        6.5 * tileSize - curveArcOffset
    ), math.pi / 2),
    PathNode(Vector2(
        0.5 * tileSize + curveArcOffset,
        7.25 * tileSize
    ), 0),
    PathNode(Vector2(
        4.5 * tileSize - curveArcOffset,
        7.25 * tileSize
    ), 0),
    PathNode(Vector2(
        4.75 * tileSize,
        7.5 * tileSize + curveArcOffset
    ), math.pi / 2),
    PathNode(Vector2(
        4.75 * tileSize,
        11.5 * tileSize - curveArcOffset
    ), math.pi / 2),
    PathNode(Vector2(
        5.5 * tileSize + curveArcOffset,
        12.25 * tileSize,
    ), 0),
    PathNode(Vector2(
        9.5 * tileSize - curveArcOffset,
        12.25 * tileSize,
    ), 0),
    PathNode(Vector2(
        9.75 * tileSize,
        12.5 * tileSize + curveArcOffset,
    ), math.pi / 2),
    PathNode(Vector2(
        9.75 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ), math.pi / 2),
    PathNode(Vector2(
        10.5 * tileSize + curveArcOffset,
        15.25 * tileSize,
    ), 0),
    PathNode(Vector2(
        11.5 * tileSize - curveArcOffset,
        15.25 * tileSize,
    ), 0),
    PathNode(Vector2(
        12.25 * tileSize,
        14.5 * tileSize - curveArcOffset,
    ), -math.pi / 2),
    PathNode(Vector2(
        12.25 * tileSize,
        8.5 * tileSize + curveArcOffset,
    ), -math.pi / 2),
    PathNode(Vector2(
        11.5 * tileSize - curveArcOffset,
        7.75 * tileSize,
    ), math.pi),
    PathNode(Vector2(
        7.5 * tileSize + curveArcOffset,
        7.75 * tileSize,
    ), math.pi),
    PathNode(Vector2(
        7.25 * tileSize,
        7.5 * tileSize - curveArcOffset,
    ), -math.pi / 2),
    PathNode(Vector2(
        7.25 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ), -math.pi / 2),
    PathNode(Vector2(
        6.5 * tileSize - curveArcOffset,
        -0.25 * tileSize,
    ), math.pi),
    PathNode(Vector2(
        4.5 * tileSize + curveArcOffset,
        -0.25 * tileSize,
    ), math.pi),
    PathNode(Vector2(
        3.75 * tileSize,
        0.5 * tileSize + curveArcOffset,
    ), math.pi / 2),
    PathNode(Vector2(
        3.75 * tileSize,
        3.5 * tileSize - curveArcOffset,
    ), math.pi / 2),
])

# Create car instance positioned at first path node
car = Car(
    path.nodes[0].pos.copy(),
    size=20,
    texturePath="img/car.png",
    textureScale=3.0,
    textureOffsetAngle=180,
    wheelAxisAspectRatio=1.8,
    initialRotation=math.pi
)

# Create driver instance
driver = Driver(
    car=car,
    path=path
)

# Create main traffic simulation instance
trafficSim = TrafficSim()

# Add driver to list
trafficSim.addDriver(driver)

# Steering wheel
STEERING_WHEEL_SIZE = WIDTH * 0.3
steeringWheel = pygame.image.load("img/steering_wheel.png")
steeringWheel = pygame.transform.scale(
    steeringWheel, (STEERING_WHEEL_SIZE, STEERING_WHEEL_SIZE)
)

# States
debug = False
focused = False
update = True

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
            if event.key == pygame.K_w:
                car.setAccelerationAmount(1)
            elif event.key == pygame.K_s:
                car.setBrakeAmount(1)
            elif event.key == pygame.K_e:
                car.reverse = not car.reverse
            elif event.key == pygame.K_f:
                debug = not debug
            elif event.key == pygame.K_g:
                focused = not focused
            elif event.key == pygame.K_q:
                update = not update
        # Check for key releases
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                car.setAccelerationAmount(0)
            elif event.key == pygame.K_s:
                car.setBrakeAmount(0)

    # Clear window
    window.fill(BLACK)

    # Get focused car offset
    if focused:
        carOffset = -car.pos + Vector2(WIDTH / 2, HEIGHT / 2)
    else:
        carOffset = Vector2(0, 0)

    # Draw the roads
    for road in roads:
        # NOTE: Currently disabling road debug because it is distracting
        road.draw(window, carOffset, False)

    # Draw path
    path.draw(window, carOffset, debug)

    # Manually update car steering based on mouse horizontal position (for now)
    car.setSteering(mouseX / WIDTH * 2 - 1)

    # Update and draw traffic
    if update:
        trafficSim.update(dt)
    trafficSim.draw(window, carOffset, debug)

    # Draw steering wheel
    # rotatedSteeringWheel = pygame.transform.rotate(
    #     steeringWheel,
    #     -car.steering * 180
    # )
    # rect = rotatedSteeringWheel.get_rect(
    #     center=(WIDTH * .5, HEIGHT - STEERING_WHEEL_SIZE / 2 - 25)
    # )
    # window.blit(rotatedSteeringWheel, rect)

    # Update window
    pygame.display.update()
    dt = clock.tick(FPS)
