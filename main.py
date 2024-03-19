from model.car import *
import pygame
import sys

WIDTH = 400
HEIGHT = 600
FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Create car instance
car = Car(
    Vector2(WIDTH/2, HEIGHT/2),
    size=15,
    texturePath="img/car.png",
    textureScale=1.35,
    textureOffsetAngle=-90,
    wheelAxisAspectRatio=1.8,
)

# Road background
road = pygame.image.load("img/road.jpg")
road = pygame.transform.scale(road, (WIDTH, HEIGHT))

getTicksLastFrame = pygame.time.get_ticks()
debug = False
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
                car.setAccelerating(True)
            elif event.key == pygame.K_s:
                car.setBraking(True)
            elif event.key == pygame.K_e:
                car.reverse = not car.reverse
            elif event.key == pygame.K_f:
                debug = not debug
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                car.setAccelerating(False)
            elif event.key == pygame.K_s:
                car.setBraking(False)

    # Clear window
    window.fill(BLACK)

    # Draw road
    window.blit(road, (0, 0))

    # Update and draw car
    car.setSteering((mouseX / WIDTH - 0.5) * 2)
    car.update(dt)
    car.draw(window, debug=debug)

    print(car.velocity)

    # Update window
    pygame.display.update()
    dt = clock.tick(FPS)