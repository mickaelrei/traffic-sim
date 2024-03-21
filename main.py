from model.car import Car
from model.driver import Driver
from model.traffic_sim import TrafficSim
from model.road import Road, StraightRoad, TopLeftCurvedRoad, TopRightCurvedRoad, BottomLeftCurvedRoad, BottomRightCurvedRoad
import pygame
import sys
import math
from pygame.math import Vector2

WIDTH = 600
HEIGHT = 800
FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Create car instance
car = Car(
    Vector2(WIDTH/4, 3*HEIGHT/4),
    size=20,
    texturePath="img/car.png",
    textureScale=1.35,
    textureOffsetAngle=-90,
    wheelAxisAspectRatio=1.8,
)

# Create driver instance
driver = Driver(
    car=car
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

# Testing curve roads
roadWidth = 110
arcOffset = 110

# Straight line roads for each of the 4 directions
roadLeft = StraightRoad(roadWidth, Vector2(0, HEIGHT/2), Vector2(WIDTH/2 - roadWidth/2 - arcOffset, HEIGHT/2))
roadRight = StraightRoad(roadWidth, Vector2(WIDTH, HEIGHT/2), Vector2(WIDTH/2 + roadWidth/2 + arcOffset, HEIGHT/2))
roadBottom = StraightRoad(roadWidth, Vector2(WIDTH/2, HEIGHT), Vector2(WIDTH/2, HEIGHT/2 + roadWidth/2 + arcOffset))
roadTop = StraightRoad(roadWidth, Vector2(WIDTH/2, 0), Vector2(WIDTH/2, HEIGHT/2 - roadWidth/2 - arcOffset))

# Curved roads, one for each of the 4 directions
curvedTopLeftRoad = TopLeftCurvedRoad(roadWidth, Vector2(WIDTH/2, HEIGHT/2), arcOffset)
curvedTopRightRoad = TopRightCurvedRoad(roadWidth, Vector2(WIDTH/2, HEIGHT/2), arcOffset)
curvedBottomLeftRoad = BottomLeftCurvedRoad(roadWidth, Vector2(WIDTH/2, HEIGHT/2), arcOffset)
curvedBottomRightRoad = BottomRightCurvedRoad(roadWidth, Vector2(WIDTH/2, HEIGHT/2), arcOffset)

# States
debug = False
focused = False
curveMode = 0

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
            elif event.key == pygame.K_c:
                curveMode = (curveMode + 1) % 4
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

    # Draw the straight roads
    roadLeft.draw(window, offset=carOffset)
    roadRight.draw(window, offset=carOffset)
    roadTop.draw(window, offset=carOffset)
    roadBottom.draw(window, offset=carOffset)

    # Draw the currently selected curved road
    if curveMode == 0:
        curvedTopLeftRoad.draw(window, offset=carOffset)
    elif curveMode == 1:
        curvedTopRightRoad.draw(window, offset=carOffset)
    elif curveMode == 2:
        curvedBottomLeftRoad.draw(window, offset=carOffset)
    else:
        curvedBottomRightRoad.draw(window, offset=carOffset)

    # Manually update car steering based on mouse horizontal position (for now)
    car.setSteering(mouseX / WIDTH * 2 - 1)

    # Update and draw traffic
    trafficSim.update(dt)
    trafficSim.draw(window, offset=carOffset, debug=debug)

    # Draw steering wheel
    rotatedSteeringWheel = pygame.transform.rotate(
        steeringWheel,
        -car.steering * 180
    )
    rect = rotatedSteeringWheel.get_rect(
        center=(WIDTH * .5, HEIGHT - STEERING_WHEEL_SIZE / 2 - 25)
    )
    window.blit(rotatedSteeringWheel, rect)

    # Update window
    pygame.display.update()
    dt = clock.tick(FPS)
