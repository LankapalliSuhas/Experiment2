# gridcracker/models.py

from typing import List, Optional, Tuple


class Cell:
    def __init__(self, row: int, col: int, value: int = 0):
        self.row = row
        self.col = col
        self.value = value

    def is_empty(self) -> bool:
        return self.value == 0

    def set(self, v: int) -> None:
        self.value = int(v)

    def clear(self) -> None:
        self.value = 0

    def __repr__(self) -> str:
        return str(self.value)


class Board:
    SIZE = 9
    BOX = 3

    def __init__(self, grid: Optional[List[List[int]]] = None):
        if grid:
            self.grid = [[int(grid[r][c]) for c in range(self.SIZE)] for r in range(self.SIZE)]
        else:
            self.grid = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]

    def get(self, r: int, c: int) -> int:
        return self.grid[r][c]

    def set(self, r: int, c: int, v: int) -> None:
        self.grid[r][c] = int(v)

    def clear(self, r: int, c: int) -> None:
        self.grid[r][c] = 0

    def row_values(self, r: int) -> List[int]:
        return self.grid[r]

    def col_values(self, c: int) -> List[int]:
        return [self.grid[r][c] for r in range(self.SIZE)]

    def box_values(self, r: int, c: int) -> List[int]:
        br = (r // self.BOX) * self.BOX
        bc = (c // self.BOX) * self.BOX
        vals = []
        for rr in range(br, br + self.BOX):
            for cc in range(bc, bc + self.BOX):
                vals.append(self.grid[rr][cc])
        return vals

    def find_empty(self) -> Optional[Tuple[int, int]]:
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] == 0:
                    return r, c
        return None

    def is_valid(self, r: int, c: int, val: int) -> bool:
        if val in self.row_values(r):
            return False
        if val in self.col_values(c):
            return False
        if val in self.box_values(r, c):
            return False
        return True

    def copy(self) -> "Board":
        return Board([row[:] for row in self.grid])

    def as_list(self) -> List[List[int]]:
        return [row[:] for row in self.grid]

    def __repr__(self) -> str:
        lines = []
        for r in range(self.SIZE):
            lines.append(" ".join(str(x) for x in self.grid[r]))
        return "\n".join(lines)


class Puzzle:
    def __init__(self, grid: Optional[List[List[int]]] = None, name: str = ""):
        self.name = name
        self.board = Board(grid)

    def load(self, grid: List[List[int]]) -> None:
        self.board = Board(grid)

    def to_list(self) -> List[List[int]]:
        return self.board.as_list()

    def is_solved(self) -> bool:
        return self.board.find_empty() is None

    def __repr__(self) -> str:
        return f"Puzzle(name={self.name})\n{repr(self.board)}"
