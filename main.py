# main.py

import argparse
import json
import sys
from gridcracker.utils.file_io import FileHandler
from gridcracker.solver import SudokuSolver
from gridcracker.generator import SudokuGenerator


def cmd_solve(args):
    # load puzzle
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                puzzle = FileHandler.load(f)
        except Exception as e:
            print(f"Error loading file '{args.input}': {e}", file=sys.stderr)
            return 2
    elif args.paste:
        try:
            puzzle = [[int(x) for x in row.split()] for row in args.paste.strip().splitlines()]
        except Exception as e:
            print(f"Invalid pasted puzzle: {e}", file=sys.stderr)
            return 2
    else:
        print("No input provided. Use --input <path> or --paste '<grid>'", file=sys.stderr)
        return 2

    solver = SudokuSolver(puzzle)
    solved = solver.solve()
    if solved:
        print("Solved puzzle:")
        for r in solved:
            print(" ".join(str(x) for x in r))
        if args.output:
            try:
                if args.output.endswith(".json"):
                    with open(args.output, "w", encoding="utf-8") as f:
                        json.dump(solved, f, indent=2)
                else:
                    FileHandler.save_text(solved, args.output)
                print(f"Saved solved puzzle to {args.output}")
            except Exception as e:
                print(f"Failed to save to '{args.output}': {e}", file=sys.stderr)
                return 3
        return 0
    else:
        print("Could not solve the provided puzzle.", file=sys.stderr)
        return 1


def cmd_generate(args):
    gen = SudokuGenerator(difficulty=args.difficulty)
    puzzles = [gen.generate() for _ in range(args.count)]
    for i, p in enumerate(puzzles, start=1):
        print(f"\n--- Puzzle #{i} ({args.difficulty}) ---")
        for r in p:
            print(" ".join(str(x) for x in r))
    if args.output:
        try:
            if args.output.endswith(".json"):
                # save as list of puzzles
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump({"difficulty": args.difficulty, "puzzles": puzzles}, f, indent=2)
            else:
                # append puzzles to a text file
                with open(args.output, "w", encoding="utf-8") as f:
                    for i, p in enumerate(puzzles, start=1):
                        f.write(f"# Puzzle {i} - {args.difficulty}\n")
                        for r in p:
                            f.write(" ".join(str(x) for x in r) + "\n")
                        f.write("\n")
            print(f"\nSaved generated puzzles to {args.output}")
        except Exception as e:
            print(f"Failed to save generated puzzles: {e}", file=sys.stderr)
            return 3
    return 0


def cmd_save(args):
    if not args.name:
        print("Provide a name for the saved puzzle with --name", file=sys.stderr)
        return 2
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                puzzle = FileHandler.load(f)
        except Exception as e:
            print(f"Error loading file '{args.input}': {e}", file=sys.stderr)
            return 2
        try:
            FileHandler.save_json(puzzle, args.storage or "data/saved_puzzles.json", args.name)
            print(f"Saved puzzle '{args.name}' into {args.storage or 'data/saved_puzzles.json'}")
            return 0
        except Exception as e:
            print(f"Failed to save puzzle: {e}", file=sys.stderr)
            return 3
    else:
        print("No input file to save. Use --input <path>", file=sys.stderr)
        return 2


def main():
    parser = argparse.ArgumentParser(prog="GridCracker", description="GridCracker CLI - solve and generate Sudoku puzzles.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    solve_p = sub.add_parser("solve", help="Solve a Sudoku puzzle")
    solve_p.add_argument("--input", "-i", help="Path to puzzle file (.txt or .json)")
    solve_p.add_argument("--paste", "-p", help="Paste puzzle text (9 lines of 9 numbers separated by spaces)")
    solve_p.add_argument("--output", "-o", help="Path to save solved puzzle (txt or .json)")

    gen_p = sub.add_parser("generate", help="Generate Sudoku puzzles")
    gen_p.add_argument("--difficulty", "-d", choices=["Easy", "Medium", "Hard"], default="Medium")
    gen_p.add_argument("--count", "-c", type=int, default=1, help="Number of puzzles to generate")
    gen_p.add_argument("--output", "-o", help="Path to save generated puzzles (txt or .json)")

    save_p = sub.add_parser("save", help="Save a puzzle into saved_puzzles.json")
    save_p.add_argument("--input", "-i", help="Path to puzzle file to save (.txt or .json)")
    save_p.add_argument("--name", "-n", help="Name/key to save puzzle under")
    save_p.add_argument("--storage", "-s", help="Storage JSON path (default: data/saved_puzzles.json)")

    args = parser.parse_args()

    if args.cmd == "solve":
        rc = cmd_solve(args)
        sys.exit(rc)
    elif args.cmd == "generate":
        rc = cmd_generate(args)
        sys.exit(rc)
    elif args.cmd == "save":
        rc = cmd_save(args)
        sys.exit(rc)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
