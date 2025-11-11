# app/streamlit_app.py

import streamlit as st
import json
import time
import numpy as np
from gridcracker.solver import SudokuSolver
from gridcracker.generator import SudokuGenerator
from gridcracker.utils.file_io import FileHandler

# --- Streamlit App Config ---
st.set_page_config(page_title="GridCracker", layout="wide", page_icon="🧩")

# --- Header ---
st.markdown(
    """
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            color: #4CAF50;
            text-shadow: 1px 1px 3px #00000033;
        }
        .sub-title {
            text-align: center;
            color: #666;
            font-size: 1.1rem;
        }
        .stButton > button {
            width: 100%;
            font-size: 1rem;
            border-radius: 10px;
        }
        .result-table {
            text-align: center;
            font-size: 1.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='main-title'>🧩 GridCracker</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>An AI-powered Sudoku Solver and Generator built using Python, OOPs, and Streamlit</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🧠 Solve Sudoku", "🎲 Generate Sudoku", "📁 Load & Save"])

# --- Solve Sudoku Tab ---
with tab1:
    st.header("🧠 Solve Sudoku Puzzle")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload Sudoku File (.txt or .json)", type=["txt", "json"])
        manual_input = st.text_area(
            "Or Paste Sudoku Grid (use 0 for blanks, 9 rows of 9 numbers separated by spaces)",
            height=250,
            placeholder="Example:\n0 3 0 0 7 0 0 0 1\n6 0 0 0 0 0 4 0 0\n...",
        )

    with col2:
        st.info("💡 Tip: Try loading a puzzle from the 'Load & Save' tab if you have saved puzzles!")

    puzzle = None
    if uploaded_file:
        puzzle = FileHandler.load(uploaded_file)
    elif manual_input.strip():
        try:
            puzzle = [[int(x) for x in row.split()] for row in manual_input.strip().split("\n")]
        except ValueError:
            st.error("Invalid Sudoku format. Please enter 9 rows with 9 numbers each (0–9).")

    if st.button("🧩 Solve Puzzle"):
        if puzzle:
            with st.spinner("Solving Sudoku..."):
                solver = SudokuSolver(puzzle)
                solved = solver.solve()
                time.sleep(1.5)
            if solved:
                st.success("✅ Sudoku Solved Successfully!")
                st.table(solved)
                if st.download_button(
                    "⬇️ Download Solved Puzzle (JSON)",
                    data=json.dumps(solved),
                    file_name="solved_sudoku.json",
                ):
                    st.info("Solved puzzle downloaded successfully!")
            else:
                st.error("❌ Could not solve this Sudoku.")
        else:
            st.warning("Please upload or enter a Sudoku puzzle first.")

# --- Generate Sudoku Tab ---
with tab2:
    st.header("🎲 Generate Sudoku Puzzle")

    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.select_slider("Select Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    with col2:
        num_puzzles = st.number_input("How many puzzles to generate?", 1, 5, 1)

    if st.button("✨ Generate Puzzle"):
        with st.spinner("Generating Sudoku Puzzle..."):
            generator = SudokuGenerator(difficulty=difficulty)
            puzzles = [generator.generate() for _ in range(num_puzzles)]
            time.sleep(1.5)

        for i, puzzle in enumerate(puzzles):
            st.success(f"{difficulty} Puzzle #{i + 1}")
            st.table(np.array(puzzle))
            st.download_button(
                f"⬇️ Download Puzzle #{i + 1} (JSON)",
                data=json.dumps(puzzle),
                file_name=f"{difficulty.lower()}_puzzle_{i + 1}.json",
            )

# --- Load & Save Tab ---
with tab3:
    st.header("📁 Load or Save Sudoku")

    st.subheader("💾 Save Current Puzzle")
    save_name = st.text_input("Enter puzzle name to save", "my_saved_puzzle")

    if st.button("💾 Save to JSON"):
        try:
            if puzzle:
                FileHandler.save_json(puzzle, f"data/saved_puzzles.json", save_name)
                st.success(f"Puzzle '{save_name}' saved successfully!")
            else:
                st.warning("No puzzle to save! Generate or solve one first.")
        except Exception as e:
            st.error(f"Error while saving puzzle: {e}")

    st.subheader("📂 Load Saved Puzzles")
    try:
        saved_data = FileHandler.load_json("data/saved_puzzles.json")
        saved_keys = list(saved_data.keys())
        if saved_keys:
            selected = st.selectbox("Select a saved puzzle", saved_keys)
            if st.button("📤 Load Puzzle"):
                st.success(f"Loaded puzzle: {selected}")
                st.table(np.array(saved_data[selected]))
        else:
            st.info("No saved puzzles found.")
    except FileNotFoundError:
        st.info("No saved puzzles file found yet. Save one to create it.")

st.markdown("---")
st.caption("🧩 Built with ❤️ using Python, Streamlit, and classic Sudoku logic.")
