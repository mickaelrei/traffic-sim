from pygame.event import Event
from model.app import PygameApp
from model.road import RoadLine
import pygame
from pygame.math import Vector2

BLACK = (0, 0, 0)
GREY = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
GREEN = (0, 255, 0)


class MapEditorApp(PygameApp):
    def __init__(self, width: int, height: int, fps: float = 60) -> None:
        super().__init__(width, height, fps)

        # Tile size for user visual help
        self.tileSize = 60

        # List of road lines
        self.roadLines: list[RoadLine] = []

        # Camera position
        self.cameraPos = Vector2(0)

        # Mouse position
        self.mousePos = Vector2(0)

        # Last mouse click pos
        self.lastClickPos: Vector2 | None = None

        # States
        self.mouseDown = False
        self.shiftDown = False

    # Clamps any world position to the center of its correspondent tile
    def worldToTile(self, v: Vector2) -> Vector2:
        x = v.x // self.tileSize * self.tileSize + self.tileSize / 2
        y = v.y // self.tileSize * self.tileSize + self.tileSize / 2
        return Vector2(x, y)

    # Converts a world position (x, y) to a tile index (i, j)
    def tileIndexFromWorldPos(self, v: Vector2) -> Vector2:
        return Vector2(v.x // self.tileSize, v.y // self.tileSize)

    # Converts a tile index (i, j) to a world position (x, y)
    def worldPosFromTileIndex(self, v: Vector2) -> Vector2:
        # Need to add half a tile so it is centered
        return Vector2(v.x * self.tileSize, v.y * self.tileSize) + Vector2(self.tileSize / 2)

    # Add a new road line, given start and end world points
    def addRoadLine(self, endWorld: Vector2) -> None:
        # Make sure user can't create diagonal road lines
        diff = endWorld - self.lastClickPos
        tileIndex = self.tileIndexFromWorldPos(diff)
        if diff.x != 0 and diff.y != 0:
            if abs(diff.x) > abs(diff.y):
                tileIndex.y = 0
            else:
                tileIndex.x = 0
        startTileIndex = self.tileIndexFromWorldPos(
            self.lastClickPos - self.cameraPos)
        endTileIndex = startTileIndex + tileIndex

        # Make sure this road line is valid
        # Invalid reasons:
        # - start and end are the same
        # - duplicate (start and end coincide with start and end or vice-versa)
        # - road overlaps another road with same direction
        if startTileIndex == endTileIndex:
            return

        # Check if its a duplicate of this road
        for roadLine in self.roadLines:
            if (roadLine.start == startTileIndex and roadLine.end == endTileIndex) or (
                roadLine.start == endTileIndex and roadLine.end == startTileIndex
            ):
                return

        # Check for road overlaps
        overlaps = -1
        overlapping = True
        while overlapping:
            overlaps += 1
            overlapping = False
            for roadLine in self.roadLines:
                # Check if its a duplicate of this road
                if (roadLine.start == startTileIndex and roadLine.end == endTileIndex) or (
                    roadLine.start == endTileIndex and roadLine.end == startTileIndex
                ):
                    break
                # Get 2 roads directions
                myDirection = (endTileIndex - startTileIndex).normalize()
                otherDirection = (roadLine.end - roadLine.start).normalize()

                # Check if these 2 roads are overlapping
                if abs(myDirection.x) == abs(otherDirection.x) and myDirection.x != 0:
                    # Both are horizontal, check if same y
                    if startTileIndex.y != roadLine.start.y:
                        continue

                    # Check for overlap
                    myMin = min(startTileIndex.x, endTileIndex.x)
                    myMax = max(startTileIndex.x, endTileIndex.x)
                    otherMin = min(roadLine.start.x, roadLine.end.x)
                    otherMax = max(roadLine.start.x, roadLine.end.x)
                    if (myMin <= otherMin <= myMax) or (otherMin <= myMin <= otherMax):
                        # There is overlap, remove other and create new one from overall min and max
                        overallMin = min(myMin, otherMin)
                        overallMax = max(myMax, otherMax)
                        self.roadLines.remove(roadLine)

                        # Update start and end
                        startTileIndex = Vector2(overallMin, startTileIndex.y)
                        endTileIndex = Vector2(overallMax, startTileIndex.y)

                        # Add new road
                        self.roadLines.append(
                            RoadLine(startTileIndex, endTileIndex))
                        overlapping = True
                        break
                elif abs(myDirection.y) == abs(otherDirection.y):
                    # Both are vertical, check if same x
                    if startTileIndex.x != roadLine.start.x:
                        continue

                    # Check for overlap
                    myMin = min(startTileIndex.y, endTileIndex.y)
                    myMax = max(startTileIndex.y, endTileIndex.y)
                    otherMin = min(roadLine.start.y, roadLine.end.y)
                    otherMax = max(roadLine.start.y, roadLine.end.y)
                    if (myMin <= otherMin <= myMax) or (otherMin <= myMin <= otherMax):
                        # There is overlap, remove other and create new one from overall min and max
                        overallMin = min(myMin, otherMin)
                        overallMax = max(myMax, otherMax)
                        self.roadLines.remove(roadLine)

                        # Update start and end
                        startTileIndex = Vector2(startTileIndex.x, overallMin)
                        endTileIndex = Vector2(startTileIndex.x, overallMax)

                        # Add new road
                        self.roadLines.append(
                            RoadLine(startTileIndex, endTileIndex))
                        overlapping = True
                        break

        # If overlapped even once, don't add new road line
        if overlaps > 0:
            return

        # If got here, road line is valid
        self.roadLines.append(RoadLine(startTileIndex, endTileIndex))

    # Function that returns whether a list of road lines represents a valid road map
    # For a road map to be valid, all roads' start/end must coincide with another road
    def isRoadMapValid(self) -> bool:
        if len(self.roadLines) == 0:
            return False

        for road in self.roadLines:
            # Check if start coincides with any other road
            startCoincides = False
            endCoincides = False
            for otherRoad in self.roadLines:
                if road == otherRoad:
                    continue

                # Go in every tile for this road and check if road.start is in it
                direction = (otherRoad.end - otherRoad.start).normalize()
                length = (otherRoad.end - otherRoad.start).length()
                p = otherRoad.start.copy()
                for i in range(int(length)+1):
                    if road.start == p:
                        startCoincides = True
                    if road.end == p:
                        endCoincides = True
                    p += direction

                # If both coincide, skip testing next roads
                if startCoincides and endCoincides:
                    break

            # If any doesn't coincide, road is not valid
            if not startCoincides or not endCoincides:
                return False

        # If got here, road is valid
        return True

    def onEvent(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            if event.key == pygame.K_LSHIFT:
                self.shiftDown = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.shiftDown = False
        elif (
            event.type == pygame.MOUSEMOTION
            and self.mouseDown
            and self.shiftDown
            and self.lastClickPos == None
        ):
            self.cameraPos += Vector2(event.rel)
        elif event.type == pygame.MOUSEWHEEL:
            self.tileSize = max(5, self.tileSize + event.y)

    def onUpdate(self, dt: float) -> None:
        # Get mouse pos
        mousePos = Vector2(pygame.mouse.get_pos())

        # Mouse clamped to tile
        camX = -self.cameraPos.x % self.tileSize
        camY = -self.cameraPos.y % self.tileSize
        camTileOffset = Vector2(camX, camY)
        tiledMousePos = self.worldToTile(
            mousePos + camTileOffset) - camTileOffset

        # Get mouse buttons state
        left, _, __ = pygame.mouse.get_pressed(3)

        # Check for changes in mouseDown
        if self.mouseDown and not left:
            # Mouse was pressed and now is released, handle button up
            if self.lastClickPos != None:
                self.addRoadLine(tiledMousePos)
            self.lastClickPos = None
        elif not self.mouseDown and left:
            # Mouse was not pressed and is pressed, handle button down
            if not self.shiftDown:
                self.lastClickPos = tiledMousePos
        self.mouseDown = left

        # Clear window
        self.window.fill(BLACK)

        # Draw grid lines
        cameraTileX = int(-self.cameraPos.x / self.tileSize)
        cameraTileY = int(-self.cameraPos.y / self.tileSize)
        tilesX = int(self.width / self.tileSize)
        tilesY = int(self.height / self.tileSize)
        # Horizontal
        for i in range(cameraTileY - 2, cameraTileY + tilesY + 2):
            pygame.draw.line(
                self.window,
                GREY,
                (0, i * self.tileSize + self.cameraPos.y),
                (self.width, i * self.tileSize + self.cameraPos.y),
            )
        # Vertical
        for i in range(cameraTileX - 2, cameraTileX + tilesX + 2):
            pygame.draw.line(
                self.window,
                GREY,
                (i * self.tileSize + self.cameraPos.x, 0),
                (i * self.tileSize + self.cameraPos.x, self.height),
            )

        # Draw existing road lines
        for roadLine in self.roadLines:
            # Convert road start to world coordinates
            startWorld = self.worldPosFromTileIndex(
                roadLine.start,
            ) + self.cameraPos
            # Convert road end to world coordinates
            endWorld = self.worldPosFromTileIndex(
                roadLine.end,
            ) + self.cameraPos

            # Draw line from start to end
            pygame.draw.line(
                self.window,
                WHITE,
                startWorld,
                endWorld,
                3,
            )

            # Draw red circle at line start
            pygame.draw.circle(
                self.window,
                RED,
                startWorld,
                self.tileSize / 4,
            )

            # Draw green circle at line end
            pygame.draw.circle(
                self.window,
                GREEN,
                endWorld,
                self.tileSize / 8,
            )

        # If drawing line, draw current line
        if self.lastClickPos != None:
            # Make sure user can't create diagonal road lines
            diff = tiledMousePos - self.lastClickPos
            tileIndex = self.tileIndexFromWorldPos(diff)
            if diff.x != 0 and diff.y != 0:
                if abs(diff.x) > abs(diff.y):
                    tileIndex.y = 0
                else:
                    tileIndex.x = 0

            # Draw line from last click pos to current click pos
            pygame.draw.line(
                self.window,
                ORANGE,
                self.lastClickPos,
                self.lastClickPos +
                self.worldPosFromTileIndex(tileIndex)
                - Vector2(self.tileSize / 2),
            )
