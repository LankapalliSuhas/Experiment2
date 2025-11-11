# gridcracker/generator.py

import random
from typing import List
from .models import Board
from .solver import CountingSolver, SudokuSolver
import os

# optional AI helper
try:
    from joblib import load as joblib_load

    def load_ai_model(path: str):
        if os.path.exists(path):
            return joblib_load(path)
        return None

except Exception:
    joblib_load = None
    load_ai_model = lambda path: None


class SudokuGenerator:
    DIFFICULTY_REMOVALS = {
        "Easy": 36,   # number of cells to remove (approx)
        "Medium": 46,
        "Hard": 54,
    }

    def __init__(self, difficulty: str = "Medium", ai_model_path: str = "gridcracker_ai/model/sudoku_ai.joblib"):
        self.difficulty = difficulty if difficulty in self.DIFFICULTY_REMOVALS else "Medium"
        self.ai_model = None
        if joblib_load:
            try:
                self.ai_model = load_ai_model(ai_model_path)
            except Exception:
                self.ai_model = None

    def _fill_board(self, board: Board) -> bool:
        empty = board.find_empty()
        if not empty:
            return True
        r, c = empty
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if board.is_valid(r, c, num):
                board.set(r, c, num)
                if self._fill_board(board):
                    return True
                board.clear(r, c)
        return False

    def _generate_full_solution(self) -> Board:
        board = Board()
        # To speed up, fill diagonal boxes with random permutations
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for r in range(box, box + 3):
                for c in range(box, box + 3):
                    board.set(r, c, nums[idx])
                    idx += 1
        # Backtrack fill remaining
        self._fill_board(board)
        return board

    def _remove_cells(self, board: Board, removals: int) -> Board:
        attempts = removals
        while attempts > 0:
            r = random.randrange(9)
            c = random.randrange(9)
            if board.get(r, c) == 0:
                continue
            # backup
            backup = board.get(r, c)
            board.set(r, c, 0)
            # ensure uniqueness: at most 1 solution
            cs = CountingSolver(board.as_list())
            sols = cs.count_solutions(limit=2)
            if sols != 1:
                board.set(r, c, backup)
                attempts -= 1  # count as attempt but preserve value
            else:
                # successful removal
                attempts -= 1
        return board

    def _heuristic_difficulty(self, puzzle: List[List[int]]) -> str:
        """Fallback heuristic: fewer clues -> harder"""
        clues = sum(1 for r in puzzle for v in r if v != 0)
        if clues >= 36:
            return "Easy"
        if clues >= 28:
            return "Medium"
        return "Hard"

    def _ai_estimate(self, puzzle: List[List[int]]) -> str:
        if self.ai_model is None:
            return self._heuristic_difficulty(puzzle)
        try:
            # Expecting ai_model.predict to accept flattened 81-length vector(s)
            flat = [v for row in puzzle for v in row]
            pred = self.ai_model.predict([flat])
            return str(pred[0])
        except Exception:
            return self._heuristic_difficulty(puzzle)

    def generate(self) -> List[List[int]]:
        full = self._generate_full_solution()
        removals = self.DIFFICULTY_REMOVALS.get(self.difficulty, 46)
        puzzle_board = full.copy()
        puzzle_board = self._remove_cells(puzzle_board, removals)
        puzzle = puzzle_board.as_list()

        # use AI helper to possibly adjust puzzle (only estimation here)
        estimated = self._ai_estimate(puzzle)
        # If AI estimate differs, we respect explicit difficulty choice but keep estimate available
        return puzzle
