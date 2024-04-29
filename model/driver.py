# NOTE: This import is needed so a class can reference itself in type annotations
# in this example, class Driver on method Driver.update(dt: float, drivers: list[Driver])
from __future__ import annotations
import pygame
from pygame.math import Vector2
import utils
import math
from random import randint
from model.car import Car
from model.path import Path

# Number of rays the driver "shoots" to detect traffic entities
DRIVER_VIEW_NUM_RAYS = 25

# How spread are the rays the driver shoots
DRIVER_VIEW_RAY_SPREAD = math.pi * .667

# Class that represents a driver inside a car
class Driver:
    def __init__(self, car: Car, desiredVelocity: float = 70) -> None:
        # Reference to the driver's car
        self.car = car

        # How fast the driver wants the car to be
        self.desiredVelocity = desiredVelocity

        # How fast the car should be based on traffic
        self.appropriateVelocity = self.desiredVelocity

        # Driver's current path
        self.path: list[Vector2] | None = None

        # Driver's current node index in path
        self.pathNodeIndex: int | None = None

    def newPath(
        self,
        startPoint: Vector2,
        points: list[Vector2],
        nodesGraph: dict[str, list[Vector2]],
    ) -> None:
        # Clear current path and generate new one which starts on current position
        self.path = None
        while self.path == None or len(self.path) < 2:
            endIndex = randint(0, len(points) - 1)
            endPoint = points[endIndex]
            self.path = utils.A_Star(nodesGraph, startPoint, endPoint)

        # Apply smooth path curves
        self.path = utils.smoothPathCurves(self.path)

        # Reset path index
        self.pathNodeIndex = 0

    # Driver will never use both brake and accelerate pedals at the same time
    def setBrakeAmount(self, amount: float) -> None:
        # No acceleration
        self.car.setAccelerationAmount(0)
        self.car.setBrakeAmount(amount)

    # Driver will never use both brake and accelerate pedals at the same time
    def setAccelerationAmount(self, amount: float) -> None:
        # No braking
        self.car.setBrakeAmount(0)
        self.car.setAccelerationAmount(amount)

    def update(
        self,
        dt: float,
        drivers: list[Driver],
        points: list[Vector2],
        nodesGraph: dict[str, list[Vector2]],
    ) -> None:
        # TODO: Set car stats based on info such as:
        # - Cars in front
        # - Current path trajectory
        # - Traffic lights

        # If no path or already at the end of current path, set new path
        if self.path == None or self.pathNodeIndex >= len(self.path) - 1:
            # Find closest node to car's current position
            dist = 1e10
            closest = None
            for point in points:
                d = (point - self.car.pos).magnitude()
                if d < dist:
                    closest = point.copy()
                    dist = d

            # Generate new path
            self.newPath(closest, points, nodesGraph)

        # Check path status
        self.traversePath()

        # Check if there's any car in front
        self.checkCarCollisions(drivers)

        # Update car
        self.car.update(dt)

    def draw(self, surface: pygame.Surface, offset: Vector2 = Vector2(0, 0), debug: bool = False) -> None:
        if self.path != None and debug:
            for point in self.path:
                pygame.draw.circle(surface, (255, 127, 0), point + offset, 5)
        self.car.draw(surface, offset, debug)

    def adjustToAppropriateSpeed(self) -> None:
        if self.car.velocity < self.appropriateVelocity:
            self.setAccelerationAmount(0.5)
        else:
            self.setBrakeAmount(0.5)

    def checkCarCollisions(self, drivers: list[Driver]) -> None:
        myCar = self.car
        for driver in drivers:
            if driver == self:
                continue

            # Check if car is in front of this car for at least 50 units
            # ----------------------------------------------------------
            otherCar = driver.car

            # Check if this car and other car are both in similar direction
            # NOTE: This check prevents unnecessary braking when seeing cars coming the other way
            angleDiff = myCar.rotation - otherCar.rotation
            while angleDiff > 2 * math.pi:
                angleDiff -= 2 * math.pi
            while angleDiff < -2 * math.pi:
                angleDiff += 2 * math.pi
            if abs(angleDiff) > math.pi / 2:
                continue

            # Because the car can be considered as a box, check collision for
            # each one of the 4 sides
            points: list[Vector2] = [
                otherCar.backLeftWheelPos(),
                otherCar.backRightWheelPos(),
                otherCar.frontRightWheelPos(),
                otherCar.frontLeftWheelPos(),
            ]
            numPoints = len(points)

            # Raycast start is this car's front
            lineStart = myCar.pos + \
                utils.directionVector(myCar.rotation) * myCar.size

            # Ray angle step
            angleStep = DRIVER_VIEW_RAY_SPREAD / DRIVER_VIEW_NUM_RAYS

            # Get minimum distance
            minDistance = 1e6
            for i in range(DRIVER_VIEW_NUM_RAYS):
                # Calculate new angle
                angle = myCar.rotation - DRIVER_VIEW_RAY_SPREAD / 2 + i * angleStep
                lineEnd = lineStart + utils.directionVector(angle) * 1500

                for j in range(numPoints):
                    p1 = points[j % numPoints]
                    p2 = points[(j + 1) % numPoints]

                    # Get intersection point
                    intersec = utils.lineLineIntersection(
                        lineStart, lineEnd, p1, p2)
                    if intersec == None:
                        continue

                    # Update min distance
                    dist = (lineStart - intersec).length()
                    if dist < minDistance:
                        minDistance = dist

            # Check if distance is too close
            actualDistance = minDistance - otherCar.size * otherCar.wheelAxisAspectRatio
            if actualDistance < 150:
                # Interpolate appropriate velocity towards the other car's velocity
                self.appropriateVelocity = utils.lerp(
                    self.appropriateVelocity, otherCar.velocity, 0.05)

                if actualDistance < 60 and otherCar.velocity != 0 and self.appropriateVelocity / otherCar.velocity > 1:
                    # Brake based on how close from the other car we are
                    # The closer, the more is needed to brake
                    self.setBrakeAmount((60 - actualDistance) / 250)
                    self.setAccelerationAmount(0)
            else:
                # Interpolate appropriate velocity towards desired velocity
                self.appropriateVelocity = utils.lerp(
                    self.appropriateVelocity, self.desiredVelocity, 0.01)

    def traversePath(self) -> None:
        if self.path == None or self.pathNodeIndex == None:
            return

        # Path algorithm:
        # - Adjust steering based on angle difference from current to next node
        # - TODO: If can't steer enough to next node, brake or switch to reverse

        # Adjust speed
        self.adjustToAppropriateSpeed()

        # Get next node
        nextNodeIndex = self.pathNodeIndex + 1
        nextNode = self.path[nextNodeIndex].copy()

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
                    # next node, it will probably start driving in circles and won't stop.
                    # TODO: Think of some way of adjusting the car so it can
                    # align with the next node. Possible solutions:
                    # - drive in reverse to realign
                    # - brake so the car can steer more (simulating braking in curves)
                    # - auto detonation :)
                    pass

                # Steer accordingly
                if angleDiff < math.pi:
                    self.car.setSteering(steerAmount)
                else:
                    self.car.setSteering(-steerAmount)
        else:
            # Advance to next node
            self.pathNodeIndex = nextNodeIndex
