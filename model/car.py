import pygame
import math
from pygame.math import Vector2
import utils

# Wheel to car size ratio
WHEEL_SIZE_RATIO = 0.22

# Max car steering angle, possible with low velocity
MAX_STEERING_ANGLE = math.pi * 0.17

# Min car steering angle, when at max velocity
MIN_STEERING_ANGLE = math.pi * 0.05

# Max car velocity
MAX_VELOCITY = 250

# How much a car's velocity gets affected by wheel friction to the ground
WHEEL_GROUND_FRICTION = 10

# Color for car wheel on debug mode
DEBUG_WHEEL_COLOR = (255, 0, 0)

# Color for car chassis outline on debug mode
DEBUG_CHASSIS_OUTLINE_COLOR = (255, 255, 255)

# Color for car front wheels path on debug mode
DEBUG_FRONT_WHEEL_PATH_COLOR = (0, 255, 0)

# Color for car back wheels path on debug mode
DEBUG_BACK_WHEEL_PATH_COLOR = (127, 0, 255)

# Color for car direction arrow
DEBUG_DIRECTION_ARROW_COLOR = (0, 0, 255)

# Color for arrow from car position to car rotation pivot center
DEBUG_DIRECTION_NORMAL_ARROW_COLOR = (0, 255, 0)

# How fast the car steers
STEERING_LERP_SPEED = 10

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
        wheelAxisAspectRatio: float=1,
        initialRotation: float=0
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

        # Used for lerping car steering
        self.targetSteering = self.steering

        # Current car velocity
        self.velocity = 0

        # Car rotation/inclination
        self.rotation = utils.normalizeAngle(initialRotation)

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
        self.targetSteering = utils.clamp(steering, -1, 1)
        # self.steering = utils.clamp(steering, -1, 1)

    # Set car acceleration (between 0 and 1)
    def setAccelerationAmount(self, accelerationAmount: float) -> None:
        self.accelerationAmount = utils.clamp(accelerationAmount, 0, 1)

    # Set car brake amount (between 0 and 1)
    def setBrakeAmount(self, brakeAmount: float) -> None:
        self.brakeAmount = utils.clamp(brakeAmount, 0, 1)

    # Distance between left and right wheels
    def horizontalWheelDist(self) -> float:
        return self.size

    # Distance between front and back wheels
    def verticalWheelDist(self) -> float:
        return self.size * self.wheelAxisAspectRatio

    def maxSteeringAngle(self) -> float:
        return MAX_STEERING_ANGLE + (MIN_STEERING_ANGLE - MAX_STEERING_ANGLE) * (self.velocity / MAX_VELOCITY)**2

    # Calculates current wheel angle based on steering and velocity
    def wheelAngle(self) -> float:
        return math.pi * 0.5 - self.steering * self.maxSteeringAngle()

    def frontLeftWheelPos(self) -> Vector2:
        halfX = self.verticalWheelDist() / 2
        halfY = self.horizontalWheelDist() / 2
        return self.pos + utils.rotatePointAroundPivot(Vector2(halfX, -halfY), Vector2(0, 0), self.rotation)
    
    def frontRightWheelPos(self) -> Vector2:
        halfX = self.verticalWheelDist() / 2
        halfY = self.horizontalWheelDist() / 2
        return self.pos + utils.rotatePointAroundPivot(Vector2(halfX, halfY), Vector2(0, 0), self.rotation)
    
    def backLeftWheelPos(self) -> Vector2:
        halfX = self.verticalWheelDist() / 2
        halfY = self.horizontalWheelDist() / 2
        return self.pos + utils.rotatePointAroundPivot(Vector2(-halfX, -halfY), Vector2(0, 0), self.rotation)
    
    def backRightWheelPos(self) -> Vector2:
        halfX = self.verticalWheelDist() / 2
        halfY = self.horizontalWheelDist() / 2
        return self.pos + utils.rotatePointAroundPivot(Vector2(-halfX, halfY), Vector2(0, 0), self.rotation)

    def update(self, dt: float) -> None:
        # Lerp steering towards targetSteering
        self.steering = utils.lerp(self.steering, self.targetSteering, STEERING_LERP_SPEED * dt)

        # Update velocity
        # ---------------
        # Decrease velocity based on wheel friction
        if self.velocity > 0:
            self.velocity = max(0, self.velocity - WHEEL_GROUND_FRICTION * dt)
        else:
            self.velocity = min(0, self.velocity + WHEEL_GROUND_FRICTION * dt)

        # Increase velocity based on how much acceleration
        self.velocity = utils.clamp(
            self.velocity
                + self.accelerationSpeed * self.accelerationAmount
                * (-1 if self.reverse else 1) * dt,
            -MAX_VELOCITY,
            MAX_VELOCITY
        )

        # Decrease velocity based on how much braking
        if self.velocity > 0:
            self.velocity = max(0, self.velocity - self.brakeForce * self.brakeAmount * dt)
        else:
            self.velocity = min(0, self.velocity + self.brakeForce * self.brakeAmount * dt)

        # Check if almost no steering
        if abs(self.steering) < 0.01:
            # Apply forward motion without finding rotation pivot
            self.pos += utils.directionVector(self.rotation) * self.velocity * dt
            return

        # Find rotation pivot
        carDirection = utils.directionVector(self.rotation)
        directionNormal = Vector2(-carDirection.y, carDirection.x)
        verticalWheelDist = self.verticalWheelDist()
        pivotSideDist = math.tan(-self.wheelAngle()) * verticalWheelDist / 2
        totalDist = self.horizontalWheelDist() * utils.sign(pivotSideDist) / 2 + pivotSideDist
        pivotCenter = self.pos \
                      - carDirection * verticalWheelDist / 2 \
                      - directionNormal * totalDist

        # Calculate rotation angle
        rotationAngle = -self.velocity * dt / totalDist

        # Rotate current position around pivot
        self.pos = utils.rotatePointAroundPivot(self.pos, pivotCenter, rotationAngle)
        self.rotation = utils.normalizeAngle(self.rotation + rotationAngle)

    def draw(self, surface: pygame.Surface, offset: Vector2=Vector2(0, 0), debug: bool=False) -> None:
        # Get wheel distances
        halfX = self.verticalWheelDist() / 2
        halfY = self.horizontalWheelDist() / 2
        wheelSize = self.size * WHEEL_SIZE_RATIO

        # Wheel positions
        frontLeft = self.frontLeftWheelPos()
        frontRight = self.frontRightWheelPos()
        backLeft = self.backLeftWheelPos()
        backRight = self.backRightWheelPos()

        # Check if has wheel texture
        if self.wheelTexture != None:
            # Rotate
            rotated = pygame.transform.rotate(self.wheelTexture, math.degrees(-self.rotation + math.pi * 0.5 - self.steering * MAX_STEERING_ANGLE))

            # Left wheel
            # ----------
            rect = rotated.get_rect(center = self.wheelTexture.get_rect(center = frontLeft + offset).center)
            surface.blit(rotated, rect)

            # Right wheel
            # ----------
            rect = rotated.get_rect(center = self.wheelTexture.get_rect(center = frontRight + offset).center)
            surface.blit(rotated, rect)

        # Check if has body texture
        if self.texture != None:
            # Rotate
            rotated = pygame.transform.rotate(self.texture, math.degrees(-self.rotation))
            # Position in center
            rect = rotated.get_rect(center = self.texture.get_rect(center = self.pos + offset).center)
            surface.blit(rotated, rect)

        if debug:
            # Car wheels
            # ----------
            pygame.draw.circle(surface, DEBUG_WHEEL_COLOR, frontLeft + offset, wheelSize)
            pygame.draw.circle(surface, DEBUG_WHEEL_COLOR, frontRight + offset, wheelSize)
            pygame.draw.circle(surface, DEBUG_WHEEL_COLOR, backLeft + offset, wheelSize)
            pygame.draw.circle(surface, DEBUG_WHEEL_COLOR, backRight + offset, wheelSize)

            # Car chassis outline
            # -------------------
            pygame.draw.line(surface, DEBUG_CHASSIS_OUTLINE_COLOR, backLeft + offset, frontLeft + offset)
            pygame.draw.line(surface, DEBUG_CHASSIS_OUTLINE_COLOR, frontLeft + offset, frontRight + offset)
            pygame.draw.line(surface, DEBUG_CHASSIS_OUTLINE_COLOR, frontRight + offset, backRight + offset)
            pygame.draw.line(surface, DEBUG_CHASSIS_OUTLINE_COLOR, backRight + offset, backLeft + offset)

            # Arrow pointing in car direction
            direc = utils.directionVector(self.rotation)
            utils.drawArrow(surface, self.pos + offset, self.pos + offset + direc * 75, DEBUG_DIRECTION_ARROW_COLOR)

            # Wheel path trajectory
            # ---------------------
            if abs(self.steering) < 0.01: return

            carDirection = utils.directionVector(self.rotation)
            directionNormal = Vector2(-carDirection.y, carDirection.x)
            verticalWheelDist = self.verticalWheelDist()
            pivotSideDist = math.tan(self.wheelAngle()) * verticalWheelDist / 2
            totalDist = self.horizontalWheelDist() * utils.sign(pivotSideDist) / 2 + pivotSideDist
            pivotCenter = self.pos \
                        - carDirection * verticalWheelDist / 2 \
                        + directionNormal * totalDist
            pygame.draw.circle(surface, DEBUG_FRONT_WHEEL_PATH_COLOR, pivotCenter + offset, (frontLeft - pivotCenter).length(), 1)
            pygame.draw.circle(surface, DEBUG_FRONT_WHEEL_PATH_COLOR, pivotCenter + offset, (frontRight - pivotCenter).length(), 1)
            pygame.draw.circle(surface, DEBUG_BACK_WHEEL_PATH_COLOR, pivotCenter + offset, (backLeft - pivotCenter).length(), 1)
            pygame.draw.circle(surface, DEBUG_BACK_WHEEL_PATH_COLOR, pivotCenter + offset, (backRight - pivotCenter).length(), 1)

            # Arrow pointing to pivot center
            utils.drawArrow(surface, self.pos + offset, pivotCenter + offset, DEBUG_DIRECTION_NORMAL_ARROW_COLOR)