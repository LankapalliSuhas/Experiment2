# gridcracker_ai/model/train_colab.py

"""
Colab-friendly training script to create a small placeholder AI model and save it as
`gridcracker_ai/model/sudoku_ai.joblib`.

This script synthesizes simple features from complete Sudoku solutions (flattened 81-length vectors)
and assigns a mock difficulty label based on number of removed clues. It trains a small RandomForest
classifier and saves it with joblib. Run this in Google Colab / local environment where scikit-learn
and joblib are available.
"""

import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
import os
from copy import deepcopy

# Utilities to create full solved boards (simple backtracking)
def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    def valid(b, r, c, v):
        if v in b[r]: return False
        if any(b[i][c] == v for i in range(9)): return False
        br, bc = (r//3)*3, (c//3)*3
        for i in range(br, br+3):
            for j in range(bc, bc+3):
                if b[i][j] == v:
                    return False
        return True

    def fill(b):
        for i in range(9):
            for j in range(9):
                if b[i][j] == 0:
                    nums = list(range(1,10))
                    random.shuffle(nums)
                    for n in nums:
                        if valid(b, i, j, n):
                            b[i][j] = n
                            if fill(b):
                                return True
                            b[i][j] = 0
                    return False
        return True

    fill(board)
    return board

# Create synthetic dataset
def make_dataset(n_samples=500):
    X = []
    y = []
    for _ in range(n_samples):
        full = generate_full_board()
        # pick a difficulty by number of removals
        rem = random.choices([36, 46, 54], weights=[0.4, 0.4, 0.2])[0]
        puzzle = deepcopy(full)
        removed = 0
        attempts = rem*3
        while removed < rem and attempts > 0:
            r = random.randrange(9)
            c = random.randrange(9)
            if puzzle[r][c] != 0:
                puzzle[r][c] = 0
                removed += 1
            attempts -= 1
        flat = [int(v) for row in puzzle for v in row]
        X.append(flat)
        if rem <= 36:
            y.append("Easy")
        elif rem <= 46:
            y.append("Medium")
        else:
            y.append("Hard")
    return np.array(X), np.array(y)

def train_and_save(path="sudoku_ai.joblib"):
    X, y = make_dataset(800)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    dump(clf, path)
    print(f"Saved model to {path}")

if __name__ == "__main__":
    # Save to package model path
    model_path = os.path.join(os.path.dirname(__file__), "sudoku_ai.joblib")
    train_and_save(model_path)
