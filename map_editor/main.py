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

while True:
    # Get mouse pos
    mousePos = Vector2(pygame.mouse.get_pos())

    # Mouse clamped to tile
    camX = -cameraPos.x % TILE_SIZE
    camY = -cameraPos.y % TILE_SIZE
    camTileOffset = Vector2(camX, camY)
    tiledMousePos = worldToTile(mousePos + camTileOffset) - camTileOffset
    mouseTileIndex = tileIndexFromWorldPos(mousePos)

    # Handle events
    for event in pygame.event.get():
        # If press ESC or close window, stop program
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
                print('\n\nlaele')
                print(tiledMousePos)
                print(tileIndexFromWorldPos(tiledMousePos))
                print(worldPosFromTileIndex(tileIndexFromWorldPos(tiledMousePos)))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                shiftDown = False
        elif event.type == pygame.MOUSEMOTION and mouseDown and not shiftDown and lastClickPos == None:
            cameraPos += Vector2(event.rel)

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)

    # Check for changes in mouseDown
    if mouseDown and not left:
        # Mouse was pressed and now is released, handle button up
        if lastClickPos != None:
            roadLines.append(RoadLine(tileIndexFromWorldPos(lastClickPos - cameraPos), tileIndexFromWorldPos(tiledMousePos - cameraPos)))
        lastClickPos = None
    elif not mouseDown and left:
        # Mouse was not pressed and is pressed, handle button down
        if shiftDown:
            lastClickPos = tiledMousePos
    mouseDown = left

    # Clear window
    window.fill(BLACK)

    # Draw grid lines
    # Horizontal
    cameraTileX = int(-cameraPos.x / TILE_SIZE)
    cameraTileY = int(-cameraPos.y / TILE_SIZE)
    tilesX = int(WIDTH / TILE_SIZE)
    tilesY = int(HEIGHT / TILE_SIZE)
    for i in range(cameraTileY - 1, cameraTileY + tilesY + 1):
        pygame.draw.line(window, (110, 110, 110), (0, i * TILE_SIZE + cameraPos.y), (WIDTH, i * TILE_SIZE + cameraPos.y))
    # Vertical
    for i in range(cameraTileX - 1, cameraTileX + tilesX + 1):
        pygame.draw.line(window, (110, 110, 110), (i * TILE_SIZE + cameraPos.x, 0), (i * TILE_SIZE + cameraPos.x, HEIGHT))

    # Draw current road lines
    for roadLine in roadLines:
        pygame.draw.line(window, WHITE, worldPosFromTileIndex(roadLine.start) + cameraPos, worldPosFromTileIndex(roadLine.end) + cameraPos)

    # If drawing line, draw current line
    if lastClickPos != None:
        # Clamp tiled mouse pos so the road line is axis-aligned
        # TODO: This is not working. Fix it
        diff = tiledMousePos - lastClickPos
        lastTileIndex = tileIndexFromWorldPos(lastClickPos)
        currentTileIndex = tileIndexFromWorldPos(tiledMousePos)
        if abs(diff.x) > abs(diff.y):
            clamped = worldPosFromTileIndex(Vector2(currentTileIndex.x, currentTileIndex.y))
            mouseTileIndex = Vector2(mouseTileIndex.x, lastTileIndex.y)
        elif abs(diff.y) > abs(diff.x):
            clamped = worldPosFromTileIndex(Vector2(currentTileIndex.x, currentTileIndex.y))
            mouseTileIndex = Vector2(lastTileIndex.x, mouseTileIndex.y)
        print(camTileOffset)
        # pygame.draw.line(window, (0, 255, 0), worldPosFromTileIndex(mouseTileIndex), lastClickPos)
        pygame.draw.line(window, ORANGE, lastClickPos, tiledMousePos)

    pygame.display.update()
    clock.tick(FPS)