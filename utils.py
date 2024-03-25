import math
import pygame
from pygame.math import Vector2
from model.path import Path

DEFAULT_ARROW_COLOR = (255, 0, 255)

DEFAULT_TEXT_COLOR = (255, 255, 255)

PATH_CURVE_INTERMEDIATE_NODES_COUNT = 3

# Draws an arrow, given start and end points
def drawArrow(surface: pygame.Surface, start: Vector2, end: Vector2, color: tuple=None) -> None:
    if end == start: return

    if color == None:
        color = DEFAULT_ARROW_COLOR

    # Get angle between end and start
    direc = (end - start).normalize()
    angle = angleFromDirection(direc)

    # Direction of two smaller lines
    angle0 = angle + math.pi / 4
    angle1 = angle - math.pi / 4
    arrow0 = directionVector(angle0)
    arrow1 = directionVector(angle1)

    # Main arrow line
    pygame.draw.line(surface, color, start, end)
    # Small line 1
    pygame.draw.line(surface, color, end, end - arrow0 * 10)
    # Small line 2
    pygame.draw.line(surface, color, end, end - arrow1 * 10)

# Draws a text at a specified position
def drawText(surface: pygame.Surface, text: str, pos: Vector2, fontSize: int=18,
             fontType: str="comicsans", bold: bool=False, italic: bool=False,
             antiAlias: bool=False, textColor: tuple=None, bgColor: tuple=None,
             anchorX: float=0, anchorY: float=0):
    if textColor is None:
        textColor = DEFAULT_TEXT_COLOR

    font = pygame.font.SysFont(fontType, round(fontSize), bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, (pos.x + textRect.width * anchorX, pos.y + textRect.height * anchorY))

# Returns a direction vector from a given angle
# NOTE: angle is interpreted as rad
def directionVector(angle: float) -> Vector2:
    c = math.cos(angle)
    s = math.sin(angle)
    return Vector2(c, s)

def angleFromDirection(direction: Vector2) -> float:
    return math.atan2(direction.y, direction.x)

# Puts the given angle in the 0-2pi range
def normalizeAngle(angle: float) -> float:
    while angle < 0:
        angle += math.pi * 2
    while angle >= math.pi * 2:
        angle -= math.pi * 2

    return angle

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

# Returns the given path with smooth curves (more nodes on curve)
def smoothPathCurves(path: Path) -> Path:
    # If path is empty or only one node, don't do anything
    if len(path.nodes) < 2:
        return path

    # New list of nodes
    nodes: list[Vector2] = []

    # Copy of current nodes
    originalNodes = path.nodes.copy()

    # Remove node duplicates
    for i in range(len(originalNodes) - 2, -1, -1):
        if (originalNodes[i] - originalNodes[i + 1]).length() == 0:
            originalNodes.pop

    # Save last node for angle check
    lastNode: Vector2 | None = None

    i = -1
    while len(originalNodes) > 1:
        # Get current and next node
        node = originalNodes.pop(0)
        nextNode = originalNodes[0]

        # Angle between current and next nodes
        angle0 = angleFromDirection((nextNode - node).normalize())

        # Angle between last and current nodes
        if lastNode is None:
            # No last node, use same angle
            angle1 = angle0
        else:
            angle1 = angleFromDirection((node - lastNode).normalize())

        # Save list of intermediate nodes
        intermediateNodes: list[Vector2] = []

        # Check angle difference
        angleDiff = angle0 - angle1
        if abs(angleDiff) > math.pi * 0.2:
            # TODO: This is wrong, doesn't work for some curves. Fix it
            curveAngle = angle0 + math.pi / 2
            print(f'Road angle at orig node {i} = {math.degrees(curveAngle):.2f}')
            # Add nodes in between two nodes
            for j in range(PATH_CURVE_INTERMEDIATE_NODES_COUNT):
                # TODO: Calculate how much the point moves in the direction of the curve (cos() and sin() of angle for j)
                point = node + (nextNode - node) * ((j + 1) / (PATH_CURVE_INTERMEDIATE_NODES_COUNT + 1))
                intermediateNodes.append(point)# - directionVector(roadAngle) * distance * 0.125)
            lastNode = intermediateNodes[len(intermediateNodes) - 1]
        else:
            lastNode = node

        # Add current node
        nodes.append(node)

        # Add all intermediate nodes after the current
        for intermediateNode in intermediateNodes:
            nodes.append(intermediateNode)

        i += 1

    # Add last node
    nodes.append(originalNodes.pop())

    # Return new path with updated nodes
    return Path(nodes)


# Returns a path with nodes from given start and end positions
def createPath(startPos: Vector2, endPos: Vector2) -> Path:
    # TODO: Use any pathfinding algorithm on a given grid of nodes to find
    # the closest path from start to end

    nodes: list[Vector2] = []
    return Path(nodes)