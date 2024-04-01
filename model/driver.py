# NOTE: This import is needed so a class can reference itself in type annotations
# in this example, class Driver on method Driver.update(dt: float, drivers: list[Driver])
from __future__ import annotations
import pygame
from pygame.math import Vector2
import math
from model.car import Car
from model.path import Path
import utils

class Driver:
    def __init__(self, car: Car, path: Path, desiredVelocity: float=70, initialPathNodeIndex: int=0) -> None:
        self.car = car
        self.desiredVelocity = desiredVelocity
        self.path = path
        self.pathNodeIndex = initialPathNodeIndex

    def update(self, dt: float, drivers: list[Driver]) -> None:
        # TODO: Set car stats based on info such as:
        # - Cars in front
        # - Current path trajectory
        # - Traffic lights

        update = True

        if not update:
            self.car.update(dt)
            return

        # Reset stats
        self.car.setBrakeAmount(0)
        self.car.setAccelerationAmount(0)
        self.car.setSteering(0)

        # Check path status
        self.traversePath()

        # Check if there's any car in front
        self.checkCarCollisions(drivers)

        # Update car
        self.car.update(dt)

    def draw(self, surface: pygame.Surface, offset: Vector2=Vector2(0, 0), debug: bool=False) -> None:
        self.path.draw(surface, offset, debug)
        self.car.draw(surface, offset, debug)

    def adjustToDesiredSpeed(self) -> None:
        if self.car.velocity < self.desiredVelocity:
            self.car.setAccelerationAmount(0.5)
        else:
            self.car.setBrakeAmount(0.5)

    def checkCarCollisions(self, drivers: list[Driver]) -> None:
        myCar = self.car
        for driver in drivers:
            if driver == self: continue

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
                print('Opposite ways')
                continue

            # Raycast start is this car's front
            lineStart = myCar.pos + utils.directionVector(myCar.rotation) * myCar.size * myCar.wheelAxisAspectRatio

            # Number of rays
            numRays = 15
            # How spread are the rays
            raySpread = math.pi / 2
            angleStep = raySpread / numRays
            
            # Get minimum distance
            minDistance = 1e6
            for i in range(numRays):
                # Calculate new angle
                angle = myCar.rotation - raySpread / 2 + i * angleStep
                lineEnd = lineStart + utils.directionVector(angle) * 1500
                
                # Because the car can be considered as a box, check collision for
                # each one of the 4 sides
                points: list[Vector2] = [
                    otherCar.backLeftWheelPos(),
                    otherCar.backRightWheelPos(),
                    otherCar.frontRightWheelPos(),
                    otherCar.frontLeftWheelPos(),
                ]
                numPoints = len(points)

                
                for i in range(numPoints):
                    p1 = points[i % numPoints]
                    p2 = points[(i + 1) % numPoints]

                    # Get intersection point
                    intersec = utils.lineLineIntersection(lineStart, lineEnd, p1, p2)
                    if intersec == None: continue

                    # Update min distance
                    dist = (lineStart - intersec).length()
                    if dist < minDistance:
                        minDistance = dist

            # Check if distance is too close
            actualDistance = minDistance - otherCar.size * otherCar.wheelAxisAspectRatio
            if actualDistance < 10:
                # TODO: Brake amount is not always 100%. This needs to be based on the distance
                myCar.setBrakeAmount(1)
                myCar.setAccelerationAmount(0)

    def traversePath(self) -> None:
        if self.path == None: return

        # Path algorithm:
        # - Adjust steering based on angle difference from current to next node
        # - TODO: If can't steer enough to next node, brake or switch to reverse

        # Adjust speed
        self.adjustToDesiredSpeed()

        # Get next node
        nextNodeIndex = (self.pathNodeIndex + 1) % len(self.path.nodes)
        nextNode = self.path.nodes[nextNodeIndex]

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
                    print(f'NEED TO STEER MORE THAN MAX: {math.degrees(angleDiff)}')

                # Steer accordingly
                if angleDiff < math.pi:
                    self.car.setSteering(steerAmount)
                else:
                    self.car.setSteering(-steerAmount)
        else:
            # Advance to next node
            self.pathNodeIndex = nextNodeIndex
