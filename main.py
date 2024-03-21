from model.car import Car
from model.driver import Driver
from model.traffic_sim import TrafficSim
from model.road import Road, StraightRoad, CurveRoad
import pygame
import sys
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
    Vector2(WIDTH/2, HEIGHT/2),
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

# Road background
roadTexture = pygame.image.load("img/road.jpg")
roadTexture = pygame.transform.scale(roadTexture, (WIDTH, HEIGHT))

# Steering wheel
STEERING_WHEEL_SIZE = WIDTH * 0.3
steeringWheel = pygame.image.load("img/steering_wheel.png")
steeringWheel = pygame.transform.scale(
    steeringWheel, (STEERING_WHEEL_SIZE, STEERING_WHEEL_SIZE)
)

getTicksLastFrame = pygame.time.get_ticks()
debug = False
focused = False
while True:
    # Calculate dt
    t = pygame.time.get_ticks()
    dt = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    # Get mouse pos
    mouseX, mouseY = pygame.mouse.get_pos()

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
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

    # Draw road
    window.blit(roadTexture, carOffset)

    # Manually update main car steering for mouse control
    car.setSteering((mouseX / WIDTH - 0.5) * 2)

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
