from pygame.math import Vector2

class RoadLine:
    def __init__(self, start: Vector2, end: Vector2) -> None:
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"[{self.start.x:.0f}, {self.start.y:.0f}] - [{self.end.x:.0f}, {self.end.y:.0f}]"