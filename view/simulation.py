from model.app import PygameApp
from model.road import Road, RoadLine, roadRules
from model.driver import Driver
from model.car import Car
from model.traffic_sim import TrafficSim
import utils
import math
import pygame
import json
from random import randint
from pygame.event import Event
from pygame.math import Vector2

# Tile size
ROAD_WIDTH = 110

# Curve arc offset
CURVE_ARC_OFFSET = 45

# Pygame app to show a traffic simulation
class TrafficSimulationApp(PygameApp):
    def __init__(self, width: int, height: int, roadMapFilePath: str, numCars: int = 1, fps: float = 60) -> None:
        # Base class init
        super().__init__(width, height, fps)

        # Whether debug rendering is on
        self.debug = False

        # Whether simulation is updating (useful for pausing)
        self.update = True

        # Whether fast update is on (useful for speeding up simulation)
        self.fastUpdate = False

        # Whether a driver is currently focused
        self.isFocused = False

        # Rendering offset, serving as camera position
        self.cameraOffset = Vector2(0, 0)

        # Rendering rotation, serving as camera rotation
        self.cameraRotation = 0

        # Camera rotation direction (0 is not rotating, -1 is left and 1 is right)
        self.cameraRotateDirection = 0

        # How fast the camera rotates
        self.cameraRotateSpeed = 1

        # Currently focused driver
        self.focusedIndex = 0

        # Whether mouse left button is down
        self.leftMouseButtonDown = False

        # Traffic simulation
        self.trafficSim = TrafficSim(ROAD_WIDTH, CURVE_ARC_OFFSET, roadMapFilePath, numCars)

    def onEvent(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        # Check for key presses
        elif event.type == pygame.KEYDOWN:
            # Debug toggle
            if event.key == pygame.K_f:
                self.debug = not self.debug
            # Toggle updating
            elif event.key == pygame.K_v:
                self.update = not self.update
            # Car focus change
            elif event.key == pygame.K_z and self.isFocused:
                self.focusedIndex = (self.focusedIndex - 1) % len(self.trafficSim.drivers)
            elif event.key == pygame.K_c and self.isFocused:
                self.focusedIndex = (self.focusedIndex + 1) % len(self.trafficSim.drivers)
            elif event.key == pygame.K_x:
                if self.isFocused:
                    # Make camera stay at focused car position and rotation
                    focusedCar = self.trafficSim.drivers[self.focusedIndex].car
                    self.cameraOffset = -focusedCar.pos + Vector2(
                        self.width,
                        self.height,
                    )
                    self.cameraRotation = focusedCar.rotation + math.pi / 2
                self.isFocused = not self.isFocused
            # Camera rotation
            elif event.key == pygame.K_q:
                self.cameraRotateDirection += -1
            elif event.key == pygame.K_e:
                self.cameraRotateDirection += 1
            elif event.key == pygame.K_h:
                self.fastUpdate = not self.fastUpdate
        # Check for key releases
        elif event.type == pygame.KEYUP:
            # Camera rotation
            if event.key == pygame.K_q:
                self.cameraRotateDirection -= -1
            elif event.key == pygame.K_e:
                self.cameraRotateDirection -= 1
        # Check for mouse motion
        elif event.type == pygame.MOUSEMOTION and self.leftMouseButtonDown and not self.isFocused:
            self.cameraOffset += Vector2(event.rel).rotate(
                math.degrees(self.cameraRotation),
            )

    def onUpdate(self, dt: float) -> None:
        # Get mouse buttons state
        left, middle, right = pygame.mouse.get_pressed(3)
        self.leftMouseButtonDown = left

        # Update camera rotation (only if not focused)
        if not self.isFocused:
            self.cameraRotation += self.cameraRotateDirection * self.cameraRotateSpeed * dt

        # Get focused car offset
        if self.isFocused:
            focusedCar = self.trafficSim.drivers[self.focusedIndex].car
            worldOffset = -focusedCar.pos + Vector2(self.width, self.height)
        else:
            worldOffset = self.cameraOffset

        # Clear window
        self.window.fill((0, 0, 0))

        # Traffic drawing surface
        trafficSurface = pygame.Surface((self.width * 2, self.height * 2))

        # Draw the roads
        for road in self.trafficSim.roads:
            road.draw(trafficSurface, worldOffset, self.debug)

        if self.debug:
            for point in self.trafficSim.points:
                pygame.draw.circle(trafficSurface, (0, 127, 255), point + self.cameraOffset, 5, 2)

            for node, connections in self.trafficSim.nodesGraph.items():
                x, y = node.split("|")
                start = Vector2(int(x), int(y))
                for p in connections:
                    utils.drawArrow(trafficSurface, start + self.cameraOffset, p + self.cameraOffset, (255, 0, 127), 2)

        # Update and draw traffic
        if self.update:
            if self.fastUpdate:
                for _ in range(5):
                    self.trafficSim.update(1/self.fps)
            self.trafficSim.update(1/self.fps)
        self.trafficSim.draw(trafficSurface, worldOffset, self.debug)

        # Check if any car is focused
        if self.isFocused:
            focusedCar = self.trafficSim.drivers[self.focusedIndex].car

            # Get rotated traffic surface based on focused car
            rotatedTraffic = pygame.transform.rotate(
                trafficSurface,
                math.degrees(focusedCar.rotation + math.pi / 2),
            )
            trafficRect = rotatedTraffic.get_rect(
                center=trafficSurface.get_rect(
                    center=(
                        self.width/2,
                        self.height/2,
                    ),
                ).center,
            )
        else:
            # Get rotated traffic surface based on current camera rotation
            rotatedTraffic = pygame.transform.rotate(
                trafficSurface,
                math.degrees(self.cameraRotation),
            )
            trafficRect = rotatedTraffic.get_rect(
                center=trafficSurface.get_rect(
                    center=(
                        self.width/2,
                        self.height/2,
                    ),
                ).center,
            )

        # Draw rotated traffic surface on window
        self.window.blit(rotatedTraffic, trafficRect)

        # Draw text indicating which car is focused
        utils.drawText(
            surface=self.window,
            text=f'Focused car: {self.focusedIndex if self.isFocused else "None"}',
            pos=Vector2(5, self.height - 5),
            anchorX=0.5,
            anchorY=-0.5,
            fontSize=25,
        )
