import pygame
import sys
from road_line import RoadLine
from pygame.math import Vector2

pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)

# Tile size for user visual help
TILE_SIZE = 60

# List of road lines
roadLines: list[RoadLine] = []

# Camera position
cameraPos = Vector2(0)

# Mouse position
mousePos = Vector2(0)

# Last mouse click pos
lastClickPos: Vector2 | None = None

# States
mouseDown = False
shiftDown = False

# Clamps any world position to the center of its correspondent tile
def worldToTile(v: Vector2) -> Vector2:
    x = v.x // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2
    y = v.y // TILE_SIZE * TILE_SIZE + TILE_SIZE / 2
    return Vector2(x, y)

# Converts a world position (x, y) to a tile index (i, j)
def tileIndexFromWorldPos(v: Vector2) -> Vector2:
    return Vector2(v.x // TILE_SIZE, v.y // TILE_SIZE)

# Converts a tile index (i, j) to a world position (x, y)
def worldPosFromTileIndex(v: Vector2) -> Vector2:
    # Need to add half a tile so it is centered
    return Vector2(v.x * TILE_SIZE, v.y * TILE_SIZE) + Vector2(TILE_SIZE / 2)

# Add a new road line, given start and end world points
def addRoadLine(startWorld: Vector2, endWorld: Vector2) -> None:
    # Make sure user can't create diagonal road lines
    diff = endWorld - startWorld
    tileIndex = tileIndexFromWorldPos(diff)
    if diff.x != 0 and diff.y != 0:
        if abs(diff.x) > abs(diff.y):
            tileIndex.y = 0
        else:
            tileIndex.x = 0
    startTileIndex = tileIndexFromWorldPos(startWorld - cameraPos)
    endTileIndex = startTileIndex + tileIndex

    # Make sure this road line is valid
    # Invalid reasons:
    # - start and end are the same
    # - duplicate (start and end coincide with start and end or vice-versa)
    # - road overlaps another road with same direction
    if startTileIndex == endTileIndex:
        return

    # Check if its a duplicate of this road
    for roadLine in roadLines:
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
        for roadLine in roadLines:
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
                    roadLines.remove(roadLine)

                    # Update start and end
                    startTileIndex = Vector2(overallMin, startTileIndex.y)
                    endTileIndex = Vector2(overallMax, startTileIndex.y)

                    # Add new road
                    roadLines.append(RoadLine(startTileIndex, endTileIndex))
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
                    roadLines.remove(roadLine)

                    # Update start and end
                    startTileIndex = Vector2(startTileIndex.x, overallMin)
                    endTileIndex = Vector2(startTileIndex.x, overallMax)

                    # Add new road
                    roadLines.append(RoadLine(startTileIndex, endTileIndex))
                    overlapping = True
                    break

    # If overlapped even once, don't add new road line
    if overlaps > 0:
        return

    # If got here, road line is valid
    roadLines.append(RoadLine(startTileIndex, endTileIndex))

# Function that returns whether a list of road lines represents a valid road map
# For a road map to be valid, all roads' start/end must coincide with another road
def isRoadMapValid(lines: list[RoadLine]) -> bool:
    for road in lines:
        # Check if start coincides with any other road
        startCoincides = False
        endCoincides = False
        for otherRoad in lines:
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

while True:
    # Get mouse pos
    mousePos = Vector2(pygame.mouse.get_pos())

    # Mouse clamped to tile
    camX = -cameraPos.x % TILE_SIZE
    camY = -cameraPos.y % TILE_SIZE
    camTileOffset = Vector2(camX, camY)
    cameraTileIndex = tileIndexFromWorldPos(cameraPos)
    tiledMousePos = worldToTile(mousePos + camTileOffset) - camTileOffset
    mouseTileIndex = tileIndexFromWorldPos(mousePos)

    # Handle events
    for event in pygame.event.get():
        # If press ESC or close window, stop program
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            # TODO: Save map to file
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                shiftDown = True
            elif event.key == pygame.K_e:
                for roadLine in roadLines:
                    print(roadLine)
            elif event.key == pygame.K_f:
                print(isRoadMapValid(roadLines))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                shiftDown = False
        elif (
            event.type == pygame.MOUSEMOTION
            and mouseDown
            and shiftDown
            and lastClickPos == None
        ):
            cameraPos += Vector2(event.rel)
        elif event.type == pygame.MOUSEWHEEL:
            TILE_SIZE = max(5, TILE_SIZE + event.y)

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)

    # Check for changes in mouseDown
    if mouseDown and not left:
        # Mouse was pressed and now is released, handle button up
        if lastClickPos != None:
            addRoadLine(lastClickPos, tiledMousePos)
        lastClickPos = None
    elif not mouseDown and left:
        # Mouse was not pressed and is pressed, handle button down
        if not shiftDown:
            lastClickPos = tiledMousePos
    mouseDown = left

    # Clear window
    window.fill(BLACK)

    # Draw grid lines
    cameraTileX = int(-cameraPos.x / TILE_SIZE)
    cameraTileY = int(-cameraPos.y / TILE_SIZE)
    tilesX = int(WIDTH / TILE_SIZE)
    tilesY = int(HEIGHT / TILE_SIZE)
    # Horizontal
    for i in range(cameraTileY - 2, cameraTileY + tilesY + 2):
        pygame.draw.line(
            window,
            (50, 50, 50),
            (0, i * TILE_SIZE + cameraPos.y),
            (WIDTH, i * TILE_SIZE + cameraPos.y),
        )
    # Vertical
    for i in range(cameraTileX - 2, cameraTileX + tilesX + 2):
        pygame.draw.line(
            window,
            (50, 50, 50),
            (i * TILE_SIZE + cameraPos.x, 0),
            (i * TILE_SIZE + cameraPos.x, HEIGHT),
        )

    # Draw existing road lines
    for roadLine in roadLines:
        startWorld = worldPosFromTileIndex(roadLine.start) + cameraPos
        endWorld = worldPosFromTileIndex(roadLine.end) + cameraPos
        pygame.draw.line(window, WHITE, startWorld, endWorld, 3)
        pygame.draw.circle(window, RED, startWorld, TILE_SIZE / 4)
        pygame.draw.circle(window, (0, 255, 0), endWorld, TILE_SIZE / 8)

    # If drawing line, draw current line
    if lastClickPos != None:
        # Make sure user can't create diagonal road lines
        diff = tiledMousePos - lastClickPos
        tileIndex = tileIndexFromWorldPos(diff)
        if diff.x != 0 and diff.y != 0:
            if abs(diff.x) > abs(diff.y):
                tileIndex.y = 0
            else:
                tileIndex.x = 0
        pygame.draw.line(
            window,
            ORANGE,
            lastClickPos,
            lastClickPos + worldPosFromTileIndex(tileIndex) - Vector2(TILE_SIZE / 2),
        )

    pygame.display.update()
    clock.tick(FPS)
