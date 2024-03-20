import pygame
import math
from pygame.math import Vector2

# Wheel to car size ratio
WHEEL_SIZE_RATIO = 0.22

# Max car steering angle
MAX_STEERING_ANGLE = math.pi * 0.17

# How much a car's velocity gets affected by wheel friction to the ground
WHEEL_GROUND_FRICTION = 10

# Rotate a point around a pivot by a given angle
# Taken from: https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
# Author: Nils Pipenbrinck, Feb 13, 2010
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

# Returns -1 for negative values, +1 for positive values, and zero for x = 0
def sign(x: float) -> float:
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

# Clamps x between a minimum and maximum value
def clamp(x: float, min: float, max: float) -> float:
    if x < min:
        return min
    if x > max:
        return max
    return x

# TODO: Change this to class Vehicle, and make other inherited classes such as:
# - Car
# - Bus
# - Truck
# - Bike
#
# Vehicles can have any amount of wheels with any offset, so only passing
# wheel axis aspect ratio is not enough
class Car:
    def __init__(
        self,
        pos: Vector2,
        size: float=40,
        texturePath: str="",
        textureScale: float=1.0,
        textureOffsetAngle: float=0,
        wheelAxisAspectRatio: float=1
    ) -> None:
        # Car position
        self.pos = pos

        # Car size in pixels, for rendering purposes
        self.size = size

        # How much the car is accelerating (between 0 and 1)
        self.accelerationAmount = 0
        
        # How much the car is braking (between 0 and 1)
        self.brakeAmount = 0

        # Whether the car is in reverse gear or not
        self.reverse = False

        # How fast the car accelerates (hardcoded for now)
        self.accelerationSpeed = 70

        # How fast the car brakes (hardcoded for now)
        self.brakeForce = 105

        # Car steering amount, between -1 and 1
        self.steering = 0

        # Current car velocity
        self.velocity = 0

        # Car's max velocity (hardcoded for now)
        self.maxVelocity = 250

        # Car rotation/inclination
        self.rotation = 0

        # Car texture scale based on [size]
        self.textureScale = textureScale

        # Aspect ratio for distance between left-right wheels and front-back wheels
        self.wheelAxisAspectRatio = wheelAxisAspectRatio

        # Try loading image
        try:
            # Load
            self.texture = pygame.image.load(texturePath)
            # Rotate
            self.texture = pygame.transform.rotate(self.texture, textureOffsetAngle)
            # Resize
            texSize = Vector2(self.texture.get_size())
            texAspectRatio = texSize.y / texSize.x
            self.texture = pygame.transform.scale(
                self.texture,
                (self.size * self.textureScale,
                 self.size * self.textureScale * texAspectRatio)
            )
        except FileNotFoundError:
            print(f"Error loading texture from path \"{texturePath}\"")
            self.texture = None

        # Try to load wheel texture
        try:
            # Load
            self.wheelTexture = pygame.image.load("img/wheel.png")
            # Resize
            texSize = Vector2(self.wheelTexture.get_size())
            texAspectRatio = texSize.y / texSize.x
            self.wheelTexture = pygame.transform.scale(
                self.wheelTexture,
                (self.size * WHEEL_SIZE_RATIO,
                 self.size * WHEEL_SIZE_RATIO * texAspectRatio)
            )
        except FileNotFoundError:
            print(f"Failed loading wheel texture from path \"img/wheel.png\"")
            self.wheelTexture = None

    # Set car steering
    def setSteering(self, steering: float) -> None:
        self.steering = clamp(steering, -1, 1)

    # Set car acceleration (between 0 and 1)
    def setAccelerationAmount(self, accelerationAmount: float) -> None:
        self.accelerationAmount = clamp(accelerationAmount, 0, 1)    

    # Set car brake amount (between 0 and 1)
    def setBrakeAmount(self, brakeAmount: float) -> None:
        self.brakeAmount = clamp(brakeAmount, 0, 1)

    # Distance between left and right wheels
    def horizontalWheelDist(self) -> float:
        return self.size

    # Distance between front and back wheels
    def verticalWheelDist(self) -> float:
        return self.size * self.wheelAxisAspectRatio
        
    def direction(self) -> Vector2:
        # NOTE: Rad 0 is pointing east, but i'm considering rotation zero pointing
        # north, so offset by pi/2
        actualRotation = self.rotation + math.pi * 0.5

        # Coordinates
        x = math.cos(actualRotation)
        y = math.sin(actualRotation)

        # Negate because of pygame coordinate system
        return -Vector2(x, y)

    def update(self, dt: float) -> None:
        # Update velocity
        # ---------------

        # Decrease velocity based on wheel friction
        if self.velocity > 0:
            self.velocity = max(0, self.velocity - WHEEL_GROUND_FRICTION * dt)
        else:
            self.velocity = min(0, self.velocity + WHEEL_GROUND_FRICTION * dt)

        # Increase velocity based on how much acceleration
        self.velocity = clamp(
            self.velocity
                + self.accelerationSpeed * self.accelerationAmount
                * (-1 if self.reverse else 1) * dt,
            -self.maxVelocity,
            self.maxVelocity
        )

        # Decrease velocity based on how much braking
        if self.velocity > 0:
            self.velocity = max(0, self.velocity - self.brakeForce * self.brakeAmount * dt)
        else:
            self.velocity = min(0, self.velocity + self.brakeForce * self.brakeAmount * dt)

        # Check if almost no steering
        if abs(self.steering) < 0.01:
            # Apply forward motion without finding rotation pivot
            self.pos += self.direction() * self.velocity * dt
            return

        # Calculate wheel angle
        wheelAngle = math.pi * 0.5 - self.steering * MAX_STEERING_ANGLE

        # Find rotation pivot
        carDirection = self.direction()
        directionNormal = Vector2(-carDirection.y, carDirection.x)
        verticalWheelDist = self.verticalWheelDist()
        pivotSideDist = math.tan(wheelAngle) * verticalWheelDist / 2
        totalDist = self.horizontalWheelDist() * sign(pivotSideDist) / 2 + pivotSideDist
        pivotCenter = self.pos \
                      - carDirection * verticalWheelDist / 2 \
                      + directionNormal * totalDist

        # Calculate rotation angle
        rotationAngle = self.velocity * dt / totalDist

        # Rotate current position around pivot
        self.pos = rotatePointAroundPivot(self.pos, pivotCenter, rotationAngle)
        self.rotation += rotationAngle

    def draw(self, surface: pygame.Surface, debug: bool=False) -> None:
        # Get wheel distances
        halfX = self.horizontalWheelDist() / 2
        halfY = self.verticalWheelDist() / 2
        wheelSize = self.size * WHEEL_SIZE_RATIO

        # Wheel positions
        frontLeft = self.pos + rotatePointAroundPivot(Vector2(-halfX, -halfY), Vector2(0, 0), self.rotation)
        frontRight = self.pos + rotatePointAroundPivot(Vector2(halfX, -halfY), Vector2(0, 0), self.rotation)
        backLeft = self.pos + rotatePointAroundPivot(Vector2(-halfX, halfY), Vector2(0, 0), self.rotation)
        backRight = self.pos + rotatePointAroundPivot(Vector2(halfX, halfY), Vector2(0, 0), self.rotation)

        # Check if has wheel texture
        if self.wheelTexture != None:
            # Rotate
            rotated = pygame.transform.rotate(self.wheelTexture, math.degrees(-self.rotation - self.steering * MAX_STEERING_ANGLE))

            # Left wheel
            # ----------
            rect = rotated.get_rect(center = self.texture.get_rect(center = frontLeft).center)
            surface.blit(rotated, rect)

            # Right wheel
            # ----------
            rect = rotated.get_rect(center = self.texture.get_rect(center = frontRight).center)
            surface.blit(rotated, rect)

        # Check if has body texture
        if self.texture != None:
            # Rotate
            rotated = pygame.transform.rotate(self.texture, math.degrees(-self.rotation))
            # Position in center
            rect = rotated.get_rect(center = self.texture.get_rect(center = self.pos).center)
            surface.blit(rotated, rect)

        if debug:
            # Car wheels
            # ----------
            pygame.draw.circle(surface, (255, 0, 0), frontLeft, wheelSize)
            pygame.draw.circle(surface, (255, 0, 0), frontRight, wheelSize)
            pygame.draw.circle(surface, (255, 0, 0), backLeft, wheelSize)
            pygame.draw.circle(surface, (255, 0, 0), backRight, wheelSize)

            # Car chassis outline
            # -------------------
            pygame.draw.line(surface, (255, 255, 255), backLeft, frontLeft)
            pygame.draw.line(surface, (255, 255, 255), frontLeft, frontRight)
            pygame.draw.line(surface, (255, 255, 255), frontRight, backRight)
            pygame.draw.line(surface, (255, 255, 255), backRight, backLeft)

            # Wheel path trajectory
            # ---------------------
            wheelAngle = math.pi * 0.5 - self.steering * MAX_STEERING_ANGLE
            carDirection = self.direction()
            directionNormal = Vector2(-carDirection.y, carDirection.x)
            verticalWheelDist = self.verticalWheelDist()
            pivotSideDist = math.tan(wheelAngle) * verticalWheelDist / 2
            totalDist = self.horizontalWheelDist() * sign(pivotSideDist) / 2 + pivotSideDist
            pivotCenter = self.pos \
                        - carDirection * verticalWheelDist / 2 \
                        + directionNormal * totalDist
            pygame.draw.circle(surface, (127, 0, 255), pivotCenter, (frontLeft - pivotCenter).length(), 1)
            pygame.draw.circle(surface, (127, 0, 255), pivotCenter, (frontRight - pivotCenter).length(), 1)
            pygame.draw.circle(surface, (0, 255, 0), pivotCenter, (backLeft - pivotCenter).length(), 1)
            pygame.draw.circle(surface, (0, 255, 0), pivotCenter, (backRight - pivotCenter).length(), 1)