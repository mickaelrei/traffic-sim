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
        dist = self.car.pos.distance_to(nextNode)
        if dist > 5:
            # Get angle from car to point
            direc = (nextNode - self.car.pos).normalize()
            angle = utils.angleFromDirection(direc)
            # Check angle difference
            angleDiff = utils.normalizeAngle(angle - self.car.rotation)
            if angleDiff != 0:
                # Steer based on angle difference
                steerAmount = angleDiff / self.car.maxSteeringAngle()
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
