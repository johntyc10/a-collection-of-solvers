"""
Continuous correctness tester for FifteenPuzzleSolver.

Generates random solvable boards, solves them, then replays the returned
path to verify it actually reaches the goal. Failures are appended to
failures.json.
"""

import json
import random
import copy
import time
from pathlib import Path

from main import FifteenPuzzleSolver


class SolverTester:
    def __init__(self, rows: int = 3, cols: int = 3, failure_file: str = "failures.json"):
        self.rows = rows
        self.cols = cols
        self.failure_file = Path(failure_file)
        self.solver = FifteenPuzzleSolver()
        self.solver.x = cols
        self.solver.y = rows
        self.solver.solution = self.solver.get_default_solution()

        self.tested = 0
        self.solved = 0
        self.failures = []

        self.solve_time_ns = []
        self.solve_steps = []

        # load previous failures if any
        if self.failure_file.exists():
            try:
                with open(self.failure_file, "r", encoding="utf-8") as f:
                    self.failures = json.load(f)
            except Exception:
                self.failures = []

    # ------------------------------------------------------------------
    # Board generation
    # ------------------------------------------------------------------
    def generate_solvable_board(self, scramble_moves: int | None = None) -> list[list[str]]:
        """
        Start from the solved board and make many random legal moves.
        This guarantees solvability.
        """
        if scramble_moves is None:
            # more moves for larger boards
            scramble_moves = self.rows * self.cols * 20

        board = copy.deepcopy(self.solver.solution)

        last_dir = None
        opposite = {"U": "D", "D": "U", "L": "R", "R": "L"}

        for _ in range(scramble_moves):
            moves = self.solver.next_moves(board)
            # avoid immediate reverse to scramble better
            candidates = [m for m in moves if m[1] != opposite.get(last_dir)]
            if not candidates:
                candidates = moves
            move = random.choice(candidates)
            self.solver.apply_or_undo_move(board, move)
            last_dir = move[1]

        return board

    # ------------------------------------------------------------------
    # Path verification
    # ------------------------------------------------------------------
    def find_tile(self, board: list[list[str]], tile: str) -> tuple[int, int]:
        for i in range(self.rows):
            for j in range(self.cols):
                if board[i][j] == tile:
                    return i, j
        raise ValueError(f"Tile {tile!r} not found on board")

    def apply_solution_path(self, start_board: list[list[str]], path: list) -> tuple[bool, str]:
        """
        Replay the path returned by the solver.
        Returns (success, error_message).
        """
        board = copy.deepcopy(start_board)

        for step_idx, step in enumerate(path):
            if not (isinstance(step, (list, tuple)) and len(step) == 2):
                return False, f"Step {step_idx}: malformed step {step!r}"

            tile, direction = step
            if direction not in ("U", "D", "L", "R"):
                return False, f"Step {step_idx}: invalid direction {direction!r}"

            try:
                ty, tx = self.find_tile(board, tile)
            except ValueError as e:
                return False, f"Step {step_idx}: {e}"

            # Build the move in the format expected by apply_or_undo_move:
            # ((tile_y, tile_x), direction)
            move = ((ty, tx), direction)

            # Sanity-check that this move is currently legal
            legal_moves = self.solver.next_moves(board)
            if move not in legal_moves:
                return False, (
                    f"Step {step_idx}: move {move} is not legal.\n"
                    f"  Board:\n{self.board_to_str(board)}\n"
                    f"  Legal moves: {legal_moves}"
                )

            self.solver.apply_or_undo_move(board, move)

        # Final check
        if board != self.solver.solution:
            return False, (
                f"Path finished but board is not solved.\n"
                f"Final board:\n{self.board_to_str(board)}"
            )

        return True, ""

    @staticmethod
    def board_to_str(board: list[list[str]]) -> str:
        return "\n".join(" ".join(row) for row in board)

    # ------------------------------------------------------------------
    # Failure recording
    # ------------------------------------------------------------------
    def record_failure(self, board: list[list[str]], path, error: str):
        entry = {
            "rows": self.rows,
            "cols": self.cols,
            "board": board,
            "path": path,
            "error": error,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.failures.append(entry)
        with open(self.failure_file, "w", encoding="utf-8") as f:
            json.dump(self.failures, f, indent=2, ensure_ascii=False)
        print(f"\n*** FAILURE recorded to {self.failure_file} ***")
        print(f"Error: {error}")
        print("Board:")
        print(self.board_to_str(board))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self, max_tests: int | None = None):
        print(f"Testing {self.rows}x{self.cols} boards. Ctrl+C to stop.\n")

        try:
            while max_tests is None or self.tested < max_tests:
                board = self.generate_solvable_board()
                start_board = copy.deepcopy(board)

                # solve (solver mutates the board, so give it a copy)
                # suppress the verbose progress prints inside solve()
                import io, contextlib
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        timestamp_ns = time.time_ns()
                        path = self.solver.solve(copy.deepcopy(board))
                        single_solve_time_ns = time.time_ns() - timestamp_ns
                except Exception as e:
                    self.tested += 1
                    self.record_failure(start_board, None, f"Exception during solve: {e}")
                    self._print_stats()
                    continue

                self.tested += 1

                if not isinstance(path, list):
                    self.record_failure(start_board, path, f"solve() returned non-list: {type(path)}")
                    self._print_stats()
                    continue

                ok, err = self.apply_solution_path(start_board, path)
                if ok:
                    self.solved += 1
                    self.solve_time_ns.append(single_solve_time_ns)
                    self.solve_steps.append(len(path))
                else:
                    self.record_failure(start_board, path, err)

                self._print_stats()

        except KeyboardInterrupt:
            print("\nStopped by user.")
            self._print_stats(final=True)

    def _print_stats(self, final: bool = False):
        rate = (self.solved / self.tested * 100) if self.tested else 0.0

        if not final:
            print(
                f"{self.tested} states tested, "
                f"solve time: {self.solve_time_ns[-1] * 1e-9:.6f}s, "
                f"steps: {self.solve_steps[-1]}, "
                f"time to step ratio: {self.solve_time_ns[-1] * 1e-9 / self.solve_steps[-1]:.6f}s/step, "
                f"{rate:.1f}% success rate ({self.solved}/{self.tested})"
            )
        else:
            avg_time = (sum(self.solve_time_ns) / len(self.solve_time_ns) * 1e-9) if len(self.solve_time_ns) > 0 else 0
            avg_steps = (sum(self.solve_steps) / len(self.solve_steps)) if len(self.solve_steps) > 0 else 0

            if self.solved > 0:
                avg_time_to_step_ratio = 0
                for i in range(self.solved):
                    avg_time_to_step_ratio += (self.solve_time_ns[i] * 1e-9) / self.solve_steps[i]
                avg_time_to_step_ratio /= self.solved

            f"solve time: {self.solve_time_ns[-1] * 1e-9:.6f}s"
            print("===== STATISTICS REPORT =====")
            print(f"{self.tested} states tested")
            print(f"Average solve time: {avg_time}s")
            print(f"Average steps: {avg_steps}")
            print(f"Average time to steps ratio: {avg_time_to_step_ratio}s/step")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Continuous tester for FifteenPuzzleSolver")
    parser.add_argument("-r", "--rows", type=int, default=3, help="number of rows (default 3)")
    parser.add_argument("-c", "--cols", type=int, default=3, help="number of columns (default 3)")
    parser.add_argument("-n", "--max-tests", type=int, default=None, help="stop after N tests")
    parser.add_argument("-f", "--failure-file", default="failures.json", help="JSON file for failures")
    args = parser.parse_args()

    tester = SolverTester(rows=args.rows, cols=args.cols, failure_file=args.failure_file)
    tester.run(max_tests=args.max_tests)
