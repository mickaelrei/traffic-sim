import pygame
import math
from pygame.math import Vector2

# Aspect ratio for distance between left-right wheels and front-back wheels
WHEEL_DISTANCE_ASPECT_RATIO = 1.8

# Wheel to car size ratio
WHEEL_SIZE_RATIO = 0.1

# Max car steering angle
MAX_STEERING_ANGLE = math.pi * 0.17

def rotatePointAroundPivot(point: Vector2, pivot: Vector2, angle: float) -> Vector2:
    s = math.sin(angle)
    c = math.cos(angle)

    point = Vector2.copy(point)

    # Translate point back to origin
    point -= pivot

    # Rotate point
    newX = point.x * c - point.y * s
    newY = point.x * s + point.y * c

    # Translate point back
    return Vector2(newX, newY) + pivot

def sign(x: float) -> float:
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

class Car:
    def __init__(self, pos: Vector2, size: float=40, texturePath: str="", textureScale: float=1.0, textureOffsetAngle: float=0) -> None:
        self.pos = pos
        self.size = size
        self.steeringRotation = 0
        self.speed = 0
        self.rotation = 0
        self.textureScale = textureScale

        # Try loading image
        try:
            # Load
            self.texture = pygame.image.load(texturePath)
            # Rotate
            self.texture = pygame.transform.rotate(self.texture, textureOffsetAngle)
            # Resize
            self.texture = pygame.transform.scale(
                self.texture,
                (self.size * self.textureScale,
                 self.size * WHEEL_DISTANCE_ASPECT_RATIO * self.textureScale)
            )
        except FileNotFoundError:
            print(f"Error loading texture from path \"{texturePath}\"")
            self.texture = None

    # Distance between left and right wheels
    def horizontalWheelDist(self) -> float:
        return self.size

    # Distance between front and back wheels
    def verticalWheelDist(self) -> float:
        return self.size * WHEEL_DISTANCE_ASPECT_RATIO
        
    def direction(self) -> Vector2:
        # NOTE: Rad 0 is pointing east, but i'm considering rotation zero pointing
        # north, so offset by pi/2
        actualRotation = self.rotation + math.pi * 0.5

        # Coordinates
        x = math.cos(actualRotation)
        y = math.sin(actualRotation)

        # Negate because of pygame coordinate system
        return -Vector2(x, y)

    def update(self, dt: float, surface: pygame.Surface) -> None:
        # Check if almost no steering
        if abs(self.steeringRotation) < 0.01:
            # Apply forward motion without finding rotation pivot
            self.pos += self.direction() * self.speed * dt
            return

        # Calculate wheel angle
        wheelAngle = math.pi * 0.5 - self.steeringRotation * MAX_STEERING_ANGLE

        # Find rotation pivot
        carDirection = self.direction()
        pivotSideDist = math.tan(wheelAngle) * self.verticalWheelDist() / 2
        totalDist = self.horizontalWheelDist() * sign(pivotSideDist) / 2 + pivotSideDist
        pivotCenter = self.pos + Vector2(-carDirection.y, carDirection.x) * totalDist

        # Draw pivot center
        pygame.draw.circle(surface, (0, 255, 0), pivotCenter, 5, 1)
        pygame.draw.circle(surface, (50, 50, 50), pivotCenter, abs(totalDist), 1)

        # Calculate rotation angle
        rotationAngle = self.speed * dt / totalDist
        # Rotate current position around pivot
        self.pos = rotatePointAroundPivot(self.pos, pivotCenter, rotationAngle)
        self.rotation += rotationAngle

    def draw(self, surface: pygame.Surface) -> None:
        # Get wheel distances
        halfX = self.horizontalWheelDist() / 2
        halfY = self.verticalWheelDist() / 2
        wheelSize = self.size * WHEEL_SIZE_RATIO

        # Check if has texture
        if self.texture != None:
            # Rotate
            rotated = pygame.transform.rotate(self.texture, math.degrees(-self.rotation))
            rect = rotated.get_rect(center = self.texture.get_rect(topleft = self.pos - Vector2(halfX, halfY) * self.textureScale).center)

            surface.blit(rotated, rect)
            return
        
        # Debug lines in case of no texture
        # Front left wheel
        frontLeft = self.pos + rotatePointAroundPivot(Vector2(-halfX, -halfY), Vector2(0, 0), self.rotation)
        pygame.draw.circle(surface, (255, 0, 0), frontLeft, wheelSize)

        # Front right wheel
        frontRight = self.pos + rotatePointAroundPivot(Vector2(halfX, -halfY), Vector2(0, 0), self.rotation)
        pygame.draw.circle(surface, (255, 0, 0), frontRight, wheelSize)

        # Back left wheel
        backLeft = self.pos + rotatePointAroundPivot(Vector2(-halfX, halfY), Vector2(0, 0), self.rotation)
        pygame.draw.circle(surface, (255, 0, 0), backLeft, wheelSize)

        # Back right wheel
        backRight = self.pos + rotatePointAroundPivot(Vector2(halfX, halfY), Vector2(0, 0), self.rotation)
        pygame.draw.circle(surface, (255, 0, 0), backRight, wheelSize)

        # Outline
        pygame.draw.line(surface, (255, 255, 255), backLeft, frontLeft)
        pygame.draw.line(surface, (255, 255, 255), frontLeft, frontRight)
        pygame.draw.line(surface, (255, 255, 255), frontRight, backRight)
        pygame.draw.line(surface, (255, 255, 255), backRight, backLeft)
        pygame.draw.line(surface, (255, 255, 255),
                         backLeft + (frontLeft - backLeft) * .5,
                         backRight + (frontRight - backRight) * .5
        )
        pygame.draw.line(surface, (255, 255, 255), self.pos, frontLeft + (frontRight - frontLeft) * .5)