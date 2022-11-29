from typing import Tuple

class Entity:
    """A generic object to describe enemies, players, etc"""
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int]):
        self.x, self.y, self.char, self.color = x, y, char, color

    def move(self, dx: int, dy: int) -> None:
        """Move the entity a given amount"""
        self.x += dx
        self.y += dy
