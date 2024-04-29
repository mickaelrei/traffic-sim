import math
import pygame
from pygame.math import Vector2
from model.path import Path

# Default color for arrow (pink)
DEFAULT_ARROW_COLOR = (255, 0, 255)

# Default color for text (white)
DEFAULT_TEXT_COLOR = (255, 255, 255)


# Draws an arrow, given start and end points
def drawArrow(
    surface: pygame.Surface,
    start: Vector2,
    end: Vector2,
    color: tuple = None,
    width: float = 1,
) -> None:
    if end == start:
        return

    if color == None:
        color = DEFAULT_ARROW_COLOR

    # Get angle between end and start
    dist = (end - start).magnitude()
    direc = (end - start).normalize()
    angle = angleFromDirection(direc)

    # Direction of two smaller lines
    angle0 = angle + math.pi / 4
    angle1 = angle - math.pi / 4
    arrow0 = directionVector(angle0)
    arrow1 = directionVector(angle1)

    # Main arrow line
    pygame.draw.line(surface, color, start, end, width)
    # Small line 1
    pygame.draw.line(surface, color, end, end - arrow0 * dist * .2, width)
    # Small line 2
    pygame.draw.line(surface, color, end, end - arrow1 * dist * .2, width)


# Draws a text at a specified position
def drawText(
    surface: pygame.Surface,
    text: str,
    pos: Vector2,
    fontSize: int = 18,
    fontType: str = "comicsans",
    bold: bool = False,
    italic: bool = False,
    antiAlias: bool = False,
    textColor: tuple = None,
    bgColor: tuple = None,
    anchorX: float = 0,
    anchorY: float = 0,
):
    if textColor is None:
        textColor = DEFAULT_TEXT_COLOR

    font = pygame.font.SysFont(fontType, round(fontSize), bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    textRect.center = Vector2(
        textRect.width * anchorX,
        textRect.height * anchorY,
    ) + pos
    surface.blit(textSurface, textRect)


def drawArc(
    surface: pygame.Surface,
    color: tuple,
    center: Vector2,
    size: Vector2,
    startAngle: float,
    endAngle: float,
    width: float
) -> None:
    # Make end angle be greater than start angle
    while endAngle < startAngle:
        endAngle += 2 * math.pi

    # List of points
    points: list[Vector2] = []
    numPoints = 50
    step = (endAngle - startAngle) / numPoints
    for i in range(numPoints + 1):
        angle = startAngle + step * i
        points.append(Vector2(
            center.x + size.x * math.cos(angle),
            center.y + size.y * math.sin(angle),
        ))

    # Draw lines
    pygame.draw.lines(surface, color, False, points, width)


# Returns a direction vector from a given angle
# NOTE: angle is interpreted as rad
def directionVector(angle: float) -> Vector2:
    c = math.cos(angle)
    s = math.sin(angle)
    return Vector2(c, s)


# Returns the angle from a direction vector
def angleFromDirection(direction: Vector2) -> float:
    return math.atan2(direction.y, direction.x)


# Puts the given angle in the 0-2pi range
def normalizeAngle(angle: float) -> float:
    while angle < 0:
        angle += math.pi * 2
    while angle >= math.pi * 2:
        angle -= math.pi * 2

    return angle


# Performs linear interpolation from a to b with alpha t
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


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
def smoothPathCurves(path: list[Vector2], precedingNode: Vector2 | None = None) -> list[Vector2]:
    # If path is empty or less than 3 nodes, don't do anything
    if len(path) < 3:
        return path

    # New list of nodes
    nodes: list[Vector2] = []

    # Copy of current nodes
    originalNodes = [p.copy() for p in path]

    # Remove node duplicates
    for i in range(len(originalNodes) - 2, -1, -1):
        if (originalNodes[i] - originalNodes[i + 1]).length() == 0:
            print(f"Removed node duplicate at index {i + 1}")
            originalNodes.pop(i + 1)

    # Save last node for angle check
    # TODO: Calls to utils.smoothPathCurves() should pass the precedingNode as the following:
    #        - Find the node in the nodesGraph which connects to the first path node (path[0])
    #       for node, connections in nodesGraph:
    #           if connections.contains(path[0]):
    #               precedingNode = node
    lastNode = precedingNode

    i = -1
    while len(originalNodes) > 1:
        i += 1
        # Get current and next node
        node = originalNodes.pop(0)
        nextNode = originalNodes[0]

        # Angle between current and next nodes
        directionToNext = (nextNode - node).normalize()
        angle0 = angleFromDirection(directionToNext)

        # Angle between last and current nodes
        if lastNode is None:
            # No last node, use same angle
            angle1 = angle0
        else:
            angle1 = angleFromDirection((node - lastNode).normalize())

        # Save list of intermediate nodes
        intermediateNodes: list[Vector2] = []

        # Check angle difference
        angleDiff = normalizeAngle(angle0) - normalizeAngle(angle1)
        while angleDiff > math.pi:
            angleDiff -= 2 * math.pi
        while angleDiff < -math.pi:
            angleDiff += 2 * math.pi
        if abs(angleDiff) > math.pi * 0.2:# and abs(angleDiff) < math.pi:
            # Normalize angle diff between [-pi/4, +pi/4] range
            if angleDiff > math.pi / 4:
                angleDiff -= 2 * math.pi
            elif angleDiff < -math.pi / 4:
                angleDiff += 2 * math.pi

            # Check if to left or to right
            if angleDiff < 0:
                # To left
                normalToNext = Vector2(-directionToNext.y, directionToNext.x)
            else:
                # To right
                normalToNext = Vector2(directionToNext.y, -directionToNext.x)

            # Distance to next node
            distance = (node - nextNode).length()

            # Num of intermediate nodes based on distance to next node
            numIntermediateNodes = int(distance / 12)

            # Add nodes in between two nodes
            step = 1 / (numIntermediateNodes + 1)
            for j in range(numIntermediateNodes):
                # Calculate how much the point moves in the direction of the curve
                t = (j + 1) * step
                point = node + (nextNode - node) * t
                normalDisplacement = 0.8 * (-(t**2) + t)

                # Add new intermediate point
                intermediateNodes.append(
                    point + normalToNext * distance * normalDisplacement,
                )

            # Set last node to be the last intermediate node
            if len(intermediateNodes) > 0:
                lastNode = intermediateNodes[len(intermediateNodes) - 1]
            else:
                lastNode = node
        else:
            lastNode = node

        # Add current node
        nodes.append(node)

        # Add all intermediate nodes after the current
        for intermediateNode in intermediateNodes:
            nodes.append(intermediateNode)

    # Return new path with updated nodes
    return nodes


# Returns a path with nodes from given start and end positions
def createPath(startPos: Vector2, endPos: Vector2) -> Path:
    # TODO: Use any pathfinding algorithm on a given grid of nodes to find
    # the closest path from start to end

    nodes: list[Vector2] = []
    return Path(nodes)


# Calculates intersection between two line segments.
#
# First segment is defined as:
# - Start = [p1]
# - End   = [p2]
#
# Second segment is defined as:
# - Start = [p3]
# - End   = [p4]
#
# Returns the point of intersection, or None if no intersection
#
# Reference:
# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
def lineLineIntersection(
    p1: Vector2,
    p2: Vector2,
    p3: Vector2,
    p4: Vector2,
) -> Vector2 | None:
    t0 = (p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)
    t1 = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if t1 == 0:
        return None
    t = t0 / t1

    u0 = (p1.x - p2.x) * (p1.y - p3.y) - (p1.y - p2.y) * (p1.x - p3.x)
    u1 = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if u1 == 0:
        return None
    u = -u0 / u1

    # Both t and u need to be in [0, 1] range
    if not (t >= 0 and t <= 1 and u >= 0 and u <= 1):
        return None

    # Check if intersection point lies in line 1 or in line 2
    if t >= 0 and t <= 1:
        # Point is between p1 and p2
        return p1 + (p2 - p1) * t
    else:
        # Point is between p3 and p4
        return p3 + (p4 - p3) * u

# Converts a vector to a string, used as a key in a dict
def vecToStr(v: Vector2) -> str:
    return f"{v.x:.0f}|{v.y:.0f}"

def A_StarReconstructPath(cameFrom: dict[str, Vector2], current: Vector2) -> list[Vector2]:
    total_path = [current]
    while vecToStr(current) in cameFrom.keys():
        current = cameFrom[vecToStr(current)]
        total_path.insert(0, current)
    return total_path

# A* finds a path from start to goal.
# https://en.wikipedia.org/wiki/A*_search_algorithm
def A_Star(graph: dict[str, list[Vector2]], start: Vector2, goal: Vector2):
    # The set of discovered nodes that may need to be (re-)expanded.
    # Initially, only the start node is known.
    # This is usually implemented as a min-heap or priority queue rather than a hash-set.
    openSet = [start]

    # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from the start
    # to n currently known.
    cameFrom: dict[str, Vector2] = {}

    # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
    gScore: dict[str, float] = {}
    gScore[vecToStr(start)] = 0

    # For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
    # how cheap a path could be from start to finish if it goes through n.
    fScore: dict[str, float] = {}
    fScore[vecToStr(start)] = 0

    while len(openSet) > 0:
        # This operation can occur in O(Log(N)) time if openSet is a min-heap or a priority queue
        # current := the node in openSet having the lowest fScore[] value
        lowestFscore = 1e10
        current = None
        for node in openSet:
            nodeFscore = fScore.get(vecToStr(node), 1e10)
            if nodeFscore < lowestFscore:
                current = node
                lowestFscore = nodeFscore

        if current == goal:
            return A_StarReconstructPath(cameFrom, current)

        openSet.remove(current)
        neighbors = graph.get(vecToStr(current), [])
        for neighbor in neighbors:
            # d(current,neighbor) is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
            tentative_gScore = gScore.get(vecToStr(current), 1e10) + current.distance_to(neighbor)
            if tentative_gScore < gScore.get(vecToStr(neighbor), 1e10):
                # This path to neighbor is better than any previous one. Record it!
                cameFrom[vecToStr(neighbor)] = current
                gScore[vecToStr(neighbor)] = tentative_gScore
                fScore[vecToStr(neighbor)] = tentative_gScore + start.distance_to(neighbor)
                if neighbor not in openSet:
                    openSet.append(neighbor)

    # Open set is empty but goal was never reached
    return None