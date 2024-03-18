from model.car import *
import pygame
import sys

WIDTH = 600
HEIGHT = 600
FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

car = Car(Vector2(WIDTH/2, HEIGHT/2), size=25, texturePath="img/car.png", textureScale=1.5, textureOffsetAngle=-90)

getTicksLastFrame = pygame.time.get_ticks()
speed = 150
rotation = 0
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
                car.speed += speed
            elif event.key == pygame.K_s:
                car.speed += -speed
            elif event.key == pygame.K_a:
                car.steeringRotation += -1
            elif event.key == pygame.K_d:
                car.steeringRotation += 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                car.speed -= speed
            elif event.key == pygame.K_s:
                car.speed -= -speed
            elif event.key == pygame.K_a:
                car.steeringRotation -= -1
            elif event.key == pygame.K_d:
                car.steeringRotation -= 1

    # Clear window
    window.fill(BLACK)

    # Update and draw car
    car.steeringRotation = (mouseX / WIDTH - 0.5) * 2
    car.update(dt, window)
    car.draw(window)

    # Update window
    pygame.display.update()
    dt = clock.tick(FPS)