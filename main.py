import time
from datetime import timedelta


class FifteenPuzzleSolver():
    def __init__(self, silent: bool = False) -> None:
        self.silent = silent

    def play(self) -> None:
        self.dim, self.board = self.get_user_input()
        self.x, self.y = self.dim

        solvable = self.is_board_solvable(self.board)
        if not solvable:
            print("The board is NOT solvable. Check your input and try again.")
            return

        self.solution = self.get_default_solution()

        timestamp = time.time_ns()
        path = self.solve(self.board)
        assert isinstance(path, list)
        duration_ns = time.time_ns() - timestamp
        print(f"Finding the solution took {timedelta(seconds=duration_ns*1e-9)}.")

        print("The solution is:")
        for i in range(len(path)):
            print(" ".join(path[i]))
            if (i + 1) % 5 == 0 and (i + 1) != len(path):
                input(f"Press enter to display the next five steps ({i + 1}/{len(path)} displayed): ")

    def get_default_solution(self) -> list[list[str]]:
        default_solution = [["_" for j in range(self.x)] for i in range(self.y)]
        for i in range(self.y):
            for j in range(self.x):
                default_solution[i][j] = str(self.x * i + j + 1)
        default_solution[self.y - 1][self.x - 1] = "_"

        self.goal_pos = dict()
        for i in range(self.y):
            for j in range(self.x):
                self.goal_pos[default_solution[i][j]] = (i, j)

        return default_solution

    def count_and_merge(self, arr, l, m, r):
        # Counts in two subarrays
        n1 = m - l + 1
        n2 = r - m

        # Set up two lists for left and right halves
        left = arr[l:m + 1]
        right = arr[m + 1:r + 1]

        # Initialize inversion count (or result)
        # and merge two halves
        res = 0
        i = 0
        j = 0
        k = l
        while i < n1 and j < n2:

            # No increment in inversion count
            # if left[] has a smaller or equal element
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
                res += (n1 - i)
            k += 1

        # Merge remaining elements
        while i < n1:
            arr[k] = left[i]
            i += 1
            k += 1
        while j < n2:
            arr[k] = right[j]
            j += 1
            k += 1

        return res

    # Function to count inversions in the array
    def count_inv(self, arr, l, r):
        res = 0
        if l < r:
            m = (r + l) // 2

            # Recursively count inversions
            # in the left and right halves
            res += self.count_inv(arr, l, m)
            res += self.count_inv(arr, m + 1, r)

            # Count inversions such that greater element is in
            # the left half and smaller in the right half
            res += self.count_and_merge(arr, l, m, r)
        return res

    def count_inversions(self, arr):
        if len(arr) > 60:
            return self.count_inv(arr, 0, len(arr) - 1)

        count = 0
        for i in range(len(arr) - 1):
            for j in range(i + 1, len(arr)):
                count += int(arr[i] > arr[j])
        return count

    def is_board_solvable(self, board: list[list[str]]) -> bool:
        flattened_board = [item for sublist in board for item in sublist]
        flattened_board_without_blank = [int(item) for item in flattened_board if item != "_"]
        inversion_count = self.count_inversions(flattened_board_without_blank)

        width = self.x
        if width % 2 == 1:
            return inversion_count % 2 == 0
        else:
            blank_row_index = -1
            for i in range(len(board)):
                if "_" in board[i]:
                    blank_row_index = i
                    break
            assert blank_row_index != -1
            blank_row_from_bottom = len(board) - blank_row_index

            return (inversion_count + blank_row_from_bottom) % 2 == 1

    def next_moves(self, board: list[list[str]]) -> list[tuple[tuple[int, int], str]]:
        """Return the possible moves in a list of (move_tile_idxs, dir)"""
        blank_idx = tuple()
        for i in range(self.y):
            if "_" in board[i]:
                blank_idx = (i, board[i].index("_"))
                break

        blank_y, blank_x = blank_idx
        possible_tile_move_dirs = ["U", "D", "L", "R"]  # eg: if blank is at leftmost, then dont evaluate R (right), because no tiles can move to the right
        if blank_x <= 0:
            possible_tile_move_dirs.remove("R")
        if blank_x >= self.x - 1:
            possible_tile_move_dirs.remove("L")
        if blank_y <= 0:
            possible_tile_move_dirs.remove("D")
        if blank_y >= self.y - 1:
            possible_tile_move_dirs.remove("U")

        result = []
        if "R" in possible_tile_move_dirs:
            result.append(((blank_y, blank_x - 1), "R"))
        if "L" in possible_tile_move_dirs:
            result.append(((blank_y, blank_x + 1), "L"))
        if "D" in possible_tile_move_dirs:
            result.append(((blank_y - 1, blank_x), "D"))
        if "U" in possible_tile_move_dirs:
            result.append(((blank_y + 1, blank_x), "U"))

        return result

    def apply_or_undo_move(self, board: list[list[str]], move: tuple[tuple[int, int], str]) -> None:
        """
        Apply or undo move to the board in place. They serve the same functionality since applying and undoing move swap the two same tiles.
        """
        # Variable names are named in the logic of applying move
        move_tile_y = move[0][0]
        move_tile_x = move[0][1]
        blank_y, blank_x = self.get_blank_idx_by_move(move)

        board[move_tile_y][move_tile_x], board[blank_y][blank_x] = board[blank_y][blank_x], board[move_tile_y][move_tile_x]

    def get_blank_idx_by_move(self, move: tuple[tuple[int, int], str]) -> tuple[int, int]:
        move_tile_y = move[0][0]
        move_tile_x = move[0][1]
        direction = move[1]

        if direction == "R":
            return move_tile_y, move_tile_x + 1
        elif direction == "L":
            return move_tile_y, move_tile_x - 1
        elif direction == "D":
            return move_tile_y + 1, move_tile_x
        elif direction == "U":
            return move_tile_y - 1, move_tile_x

    def is_board_solution(self, board: list[list[str]]):
        flattened_board = [item for sublist in board for item in sublist]
        flattened_solution = [item for sublist in self.solution for item in sublist]

        for i in range(len(flattened_board)):
            if flattened_board[i] != flattened_solution[i]:
                return False
        return True

    def 線性衝突次數(self, board: list[list[str]]) -> int:
        conflicts = 0

        # rows
        for i in range(self.y):
            for c1 in range(self.x):
                t1 = board[i][c1]
                if t1 == "_" or self.goal_pos[t1][0] != i:
                    continue
                for c2 in range(c1 + 1, self.x):
                    t2 = board[i][c2]
                    if t2 == "_" or self.goal_pos[t2][0] != i:
                        continue
                    # both belong to this row; check order
                    if self.goal_pos[t1][1] > self.goal_pos[t2][1]:
                        conflicts += 1

        # columns (same idea)
        for j in range(self.x):
            for r1 in range(self.y):
                t1 = board[r1][j]
                if t1 == "_" or self.goal_pos[t1][1] != j:
                    continue
                for r2 in range(r1 + 1, self.y):
                    t2 = board[r2][j]
                    if t2 == "_" or self.goal_pos[t2][1] != j:
                        continue
                    if self.goal_pos[t1][0] > self.goal_pos[t2][0]:
                        conflicts += 1

        return conflicts

    def 迭代加深A星算法(self, board: list[list[str]], depth: int, threshold: int, path: list, last_move_tile: str, 前回のマンハッタン距離: int):  # f = g + h <= threshold
        h = 前回のマンハッタン距離 + self.線性衝突次數(board) * 2
        f = depth + h
        if f > threshold:
            return f

        if h == 0:
            return path

        if depth > self._max_depth:
            self._max_depth = depth

        min_f_gt_threshold = float("inf")
        for move in self.next_moves(board):
            move_tile_y, move_tile_x = move[0]
            move_tile = board[move_tile_y][move_tile_x]
            # skip moves that moves the same tile as last move
            if move_tile == last_move_tile:
                continue

            self._evaluated_nodes += 1
            if not self.silent:
                print("----------------------")
                print(f"Gone through {self._evaluated_nodes} nodes, max depth = {self._max_depth}")

            # calculate new manhattan distance
            # Before applying the move
            tile = board[move_tile_y][move_tile_x]
            goal_y, goal_x = self.goal_pos[tile]

            # Current contribution of this tile
            old_contrib = abs(move_tile_y - goal_y) + abs(move_tile_x - goal_x)

            # After the move the tile will be at the blank's current position
            blank_y, blank_x = self.get_blank_idx_by_move(move)
            new_contrib = abs(blank_y - goal_y) + abs(blank_x - goal_x)

            マンハッタン距離 = 前回のマンハッタン距離 - old_contrib + new_contrib

            # apply move
            self.apply_or_undo_move(board, move)
            path.append((move_tile, move[1]))  # move_tile, dir

            t = self.迭代加深A星算法(board, depth + 1, threshold, path, move_tile, マンハッタン距離)
            if isinstance(t, list):
                return t
            if t < min_f_gt_threshold:
                min_f_gt_threshold = t

            # undo
            path.pop()
            self.apply_or_undo_move(board, move)

        return min_f_gt_threshold

    def solve(self, board):
        # calculate manhattan distance + linear conflict
        board_element_coords = dict()
        target_element_coords = dict()
        for i in range(self.y):
            for j in range(self.x):
                board_element_coords[board[i][j]] = (i, j)
                target_element_coords[self.solution[i][j]] = (i, j)

        total_manhattan_dist = 0
        for i in range(self.y):
            for j in range(self.x):
                if board[i][j] == "_":
                    continue
                x1, y1 = board_element_coords[board[i][j]]
                x2, y2 = target_element_coords[board[i][j]]
                total_manhattan_dist += abs(x2 - x1) + abs(y2 - y1)

        t = total_manhattan_dist + self.線性衝突次數(board) * 2

        while not isinstance(t, list):
            self._max_depth = 0
            self._evaluated_nodes = 0
            t = self.迭代加深A星算法(board, 0, t, [], "", total_manhattan_dist)
        return t

    def get_user_input(self) -> tuple[tuple[int, int], list[list[str]]]:
        """
        Handles user input.
        Returns dimensions (x, y) and the board.
        """
        # functions
        def is_integer(string: str) -> bool:
            if not string:
                return False

            for char in string:
                if char not in "1234567890":
                    return False
            return True

        # get dimension inputs
        while 1:
            input_y = input("Input the number of rows (default 4): ").strip()
            if is_integer(input_y) and int(input_y) >= 2 or not input_y:
                break
            print("The number of rows should be a positive integer greater than 1. Please try again.")
        input_y = input_y or "4"
        y = int(input_y)
        print(f"The board will have {y} rows.")

        while 1:
            input_x = input("Input the number of columns (default 4): ").strip()
            if is_integer(input_x) and int(input_x) >= 2 or not input_x:
                break
            print("The number of columns should be a positive integer greater than 1. Please try again.")
        input_x = input_x or "4"
        x = int(input_x)
        print(f"The board will have {x} columns.")

        # more functions
        def is_valid_element(string: str) -> bool:
            for char in string:
                if char not in "1234567890_":
                    return False

            if is_integer(string):
                value = int(string)
                return 1 <= value <= x * y - 1
            else:
                return string == "_"

        def check_row_input(row_input: str, empty_count: int, inputted: set) -> tuple[bool, str]:
            _row = row_input.split(" ")

            if len(_row) != x:
                return False, "Element count does not match"

            if len(set(_row)) != len(_row):
                return False, "There are duplicate elements"

            for e in _row:
                if not is_valid_element(e):
                    return False, f"One of the elements is not between 1 and {x * y - 1}"
                if empty_count >= 1 and e == "_":
                    return False, "Board already has one empty"
                if e in inputted:
                    return False, f"Element {e} already inputted"

            return True, ""

        # get board input
        board = []
        inputted = set()
        while 1:
            board = []
            inputted = set()
            empty_count = 0
            for i in range(y):
                while 1:
                    row_input = input(f"Please input content for row {i + 1}, separated by spaces, \"_\" for empty (eg: 1 9 _ 3 14): ").strip()
                    valid, message = check_row_input(row_input, empty_count, inputted)
                    if valid:
                        break
                    print(f"{message}. Please try again.")
                row = row_input.split(" ")
                board.append(row)
                empty_count += row.count("_")
                for e in row:
                    inputted.add(e)
            if "_" in inputted:
                break
            print("Board must have at least one empty. Please try again.")

        # build target solution
        print("Using default solution (1 2 3 4 ...).")

        return (x, y), board


if __name__ == "__main__":
    solver = FifteenPuzzleSolver()

    # solver.x = 3
    # solver.y = 3
    # solver.solution = solver.get_default_solution()
    # print(
    #     solver.solve([
    #             ["1", "5", "7"],
    #             ["2", "8", "6"],
    #             ["_", "3", "4"]
    #         ]
    #     )
    # )

    # requires 52 steps to solve; is a hard starting position
    # solver.x = 4
    # solver.y = 4
    # solver.solution = solver.get_default_solution()
    # print(
    #     solver.solve([
    #             ["2", "13", "10", "6"],
    #             ["15", "3", "11", "7"],
    #             ["12", "1", "_", "5"],
    #             ["9", "8", "4", "14"]
    #         ]
    #     )
    # )

    # this takes 60 steps to solve (04:40 evaluation time)
    # 13 14 12 11
    # 10 15 7 3
    # 8 1 _ 5
    # 6 2 9 4

    solver.play()
