import math
import pygame
from pygame.math import Vector2

DEFAULT_ARROW_COLOR = (255, 0, 255)

DEFAULT_TEXT_COLOR = (255, 255, 255)

# Draws an arrow, given start and end points
def drawArrow(surface: pygame.Surface, start: Vector2, end: Vector2, color: tuple=None) -> None:
    if end == start: return

    if color == None:
        color = DEFAULT_ARROW_COLOR

    # Get angle between end and start
    direc = (end - start).normalize()
    angle = math.atan2(direc.y, direc.x)

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
