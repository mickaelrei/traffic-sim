import pygame
from pygame.math import Vector2
import math
from model.car import Car
from model.path import Path
import utils

class Driver:
    def __init__(self, car: Car, path: Path) -> None:
        self.car = car
        self.elapsedTime = 0
        self.desiredVelocity = 70
        self.path = path
        self.pathNodeIndex = 0

    def update(self, dt: float) -> None:
        # TODO: Set car stats based on info such as:
        # - Cars in front
        # - Current path trajectory
        # - Traffic lights

        update = True

        if not update:
            self.car.update(dt)
            return

        # Reset stats
        # -----------
        self.car.setBrakeAmount(0)
        self.car.setAccelerationAmount(0)
        self.car.setSteering(0)

        # Adjust to desired speed
        # -----------------------
        if self.car.velocity < self.desiredVelocity:
            self.car.setAccelerationAmount(0.5)
        else:
            self.car.setBrakeAmount(0.5)

        # Adjust steering based on angle difference from current to next node
        # -------------------------------------------------------------------
        nextNodeIndex = (self.pathNodeIndex + 1) % len(self.path.nodes)
        nextNode = self.path.nodes[nextNodeIndex]

        # Check if too far away from next node
        if self.car.pos.distance_to(nextNode) > self.car.size:
            # Get angle from car to point
            direc = (nextNode - self.car.pos).normalize()
            angle = utils.angleFromDirection(direc)
            # Check angle difference
            angleDiff = angle - self.car.rotation

            # Make the angle diff be in the [-180, 180] range, because more
            # than that means a full return, which very probably is not the case
            while angleDiff < -math.pi:
                angleDiff += 2 * math.pi
            while angleDiff > math.pi:
                angleDiff -= 2 * math.pi

            # Check if actually need to steer (angle is not zero)
            if angleDiff != 0:
                # Steer based on angle difference and car max steer
                steerAmount = angleDiff / self.car.maxSteeringAngle()

                # Check if can't steer enough
                if abs(steerAmount) > 1:
                    # NOTE: If the car can't steer enough to align with the
                    # next node, it will probably start spinning and won't stop.
                    # TODO: Think of some way of adjusting the car so it can
                    # align with the next node. Possible solutions:
                    # - drive in reverse to realign
                    # - brake so the car can steer more (simulating braking in curves)
                    # - auto detonation :)
                    print(f'NEED TO STEER MORE THAN MAX: {math.degrees(angleDiff)}')

                # Steer accordingly
                if angleDiff < math.pi:
                    self.car.setSteering(steerAmount)
                else:
                    self.car.setSteering(-steerAmount)
        else:
            # Advance to next node
            self.pathNodeIndex = nextNodeIndex

        # Update car
        # ----------
        self.car.update(dt)

    def draw(self, surface: pygame.Surface, offset: Vector2=Vector2(0, 0), debug: bool=False) -> None:
        self.car.draw(surface, offset, debug)
