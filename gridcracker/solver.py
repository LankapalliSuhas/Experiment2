# gridcracker/solver.py

from typing import List, Optional
from .models import Board
import copy


class SudokuSolver:
    def __init__(self, grid: List[List[int]]):
        self._original = Board(grid)
        self.board = self._original.copy()

    def _find_empty(self) -> Optional[tuple]:
        return self.board.find_empty()

    def _is_valid(self, r: int, c: int, val: int) -> bool:
        return self.board.is_valid(r, c, val)

    def _backtrack(self) -> bool:
        empty = self._find_empty()
        if not empty:
            return True
        r, c = empty
        for val in range(1, 10):
            if self._is_valid(r, c, val):
                self.board.set(r, c, val)
                if self._backtrack():
                    return True
                self.board.clear(r, c)
        return False

    def solve(self) -> Optional[List[List[int]]]:
        """Solve the Sudoku. Returns solved grid or None."""
        self.board = self._original.copy()
        solved = self._backtrack()
        if solved:
            return self.board.as_list()
        return None


# Utility solver that counts solutions (used by generator)
class CountingSolver(SudokuSolver):
    def __init__(self, grid):
        super().__init__(grid)
        self.count = 0
        self.limit = 2  # stop if found >= limit

    def _backtrack_count(self):
        if self.count >= self.limit:
            return
        empty = self._find_empty()
        if not empty:
            self.count += 1
            return
        r, c = empty
        for val in range(1, 10):
            if self._is_valid(r, c, val):
                self.board.set(r, c, val)
                self._backtrack_count()
                self.board.clear(r, c)
                if self.count >= self.limit:
                    return

    def count_solutions(self, limit: int = 2) -> int:
        self.count = 0
        self.limit = limit
        self.board = self._original.copy()
        self._backtrack_count()
        return self.count
