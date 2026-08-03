import copy
from collections import deque


class Node():
    def __init__(self, parent=None, move=None):
        self.parent = parent
        self.move = move


class FifteenPuzzleSolver():
    def __init__(self) -> None:
        ...

    def play(self) -> None:
        self.dim, self.board = self.get_user_input()
        self.x, self.y = self.dim

        solvable = self.is_board_solvable()
        if not solvable:
            print("The board is NOT solvable. Check your input and try again.")
            return

        self.solution = self.get_default_solution()

        path = self.迭代加深A星算法()

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
        return self.count_inv(arr, 0, len(arr) - 1)

    def is_board_solvable(self):
        flattened_board = [item for sublist in self.board for item in sublist]
        flattened_board_without_blank = [int(item) for item in flattened_board if item != "_"]
        inversion_count = self.count_inversions(flattened_board_without_blank)

        width = self.x
        if width % 2 == 1:
            return inversion_count % 2 == 0
        else:
            blank_row_index = -1
            for i in range(len(self.board)):
                if "_" in self.board[i]:
                    blank_row_index = i
                    break
            assert blank_row_index != -1
            blank_row_from_bottom = len(self.board) - blank_row_index

            return (inversion_count + blank_row_from_bottom) % 2 == 1

    def next_moves(self, board: list[list[str]]) -> list[tuple[tuple[str, str], list[list[str]]]]:
        """Return the possible moves and the board states after the moves respectively"""
        def next_move(board: list[list[str]], move_tile_idx: tuple, blank_idx: tuple, dir: str) -> tuple[tuple[str, str], list[list[str]]]:
            move_tile_y, move_tile_x = move_tile_idx
            blank_y, blank_x = blank_idx
            move_tile = board[move_tile_y][move_tile_x]
            next_board_state = copy.deepcopy(board)
            next_board_state[blank_y][blank_x], next_board_state[move_tile_y][move_tile_x] = next_board_state[move_tile_y][move_tile_x], next_board_state[blank_y][blank_x]  # swap blank and move_tile
            return (move_tile, dir), next_board_state

        blank_idx = tuple()
        for i in range(self.y):
            if "_" in board[i]:
                blank_idx = (i, board[i].index("_"))
                break

        blank_y, blank_x = blank_idx
        to_evaluate_tile_move_dir = ["U", "D", "L", "R"]  # eg: if blank is at leftmost, then dont evaluate R (right), because no tiles can move to the right
        if blank_x <= 0:
            to_evaluate_tile_move_dir.remove("R")
        if blank_x >= self.x - 1:
            to_evaluate_tile_move_dir.remove("L")
        if blank_y <= 0:
            to_evaluate_tile_move_dir.remove("D")
        if blank_y >= self.y - 1:
            to_evaluate_tile_move_dir.remove("U")

        result = []
        if "R" in to_evaluate_tile_move_dir:
            result.append(next_move(board, (blank_y, blank_x - 1), blank_idx, "R"))
        if "L" in to_evaluate_tile_move_dir:
            result.append(next_move(board, (blank_y, blank_x + 1), blank_idx, "L"))
        if "D" in to_evaluate_tile_move_dir:
            result.append(next_move(board, (blank_y - 1, blank_x), blank_idx, "D"))
        if "U" in to_evaluate_tile_move_dir:
            result.append(next_move(board, (blank_y + 1, blank_x), blank_idx, "U"))

        return result

    def is_board_solution(self, board: list[list[str]]):
        flattened_board = [item for sublist in board for item in sublist]
        flattened_solution = [item for sublist in self.solution for item in sublist]

        for i in range(len(flattened_board)):
            if flattened_board[i] != flattened_solution[i]:
                return False
        return True

    def 線性衝突次數(self, board: list[list[str]]) -> int:
        linear_conflict_count = 0

        # row
        for i in range(self.y):
            row = board[i]
            linear_conflict_count += self.count_inversions([item for item in row if item in self.solution[i]])

        # column
        for j in range(self.x):
            board_col = []
            sol_col = []
            for i in range(self.y):
                board_col.append(board[i][j])
                sol_col.append(self.solution[i][j])
            linear_conflict_count += self.count_inversions([item for item in board_col if item in sol_col])

        return linear_conflict_count

    def マンハッタン距離(self, board: list[list[str]], target: list[list[str]]) -> int:
        # TODO: incremental manhattan distance calculation
        # precompute lookup table
        board_element_coords = dict()
        target_element_coords = dict()
        for i in range(self.y):
            for j in range(self.x):
                board_element_coords[board[i][j]] = (i, j)
                target_element_coords[target[i][j]] = (i, j)

        total_manhattan_dist = 0
        for i in range(self.y):
            for j in range(self.x):
                x1, y1 = board_element_coords[board[i][j]]
                x2, y2 = target_element_coords[board[i][j]]
                total_manhattan_dist += abs(x2 - x1) + abs(y2 - y1)

        return total_manhattan_dist + self.線性衝突次數(board) * 2

    def 迭代加深A星算法(self) -> list[tuple[str, str]]:  # f = g + h <= threshold
        # TODO: Use parent pointer and reconstruct path instead of list copying
        smallest_f_gt_threshold = None
        while 1:
            layer_quantity = 1
            max_depth = 0

            stack = deque([([], self.board)])  # list of (path, board)

            threshold = smallest_f_gt_threshold or self.マンハッタン距離(self.board, self.solution)
            smallest_f_gt_threshold = None
            print("--------------")
            print(f"{threshold = }")
            while stack:
                # print(len(stack))
                top = stack.pop()
                path = top[0]
                g = len(path)
                board = top[1]
                f = g + self.マンハッタン距離(board, self.solution)

                if f - 0.000001 > threshold:  # small bias for preventing float accuracy related bugs
                    if smallest_f_gt_threshold is None or f < smallest_f_gt_threshold:
                        smallest_f_gt_threshold = f
                    continue

                if self.is_board_solution(board):
                    return path

                _next_moves = self.next_moves(board)
                for move, new_board in _next_moves:
                    if path:
                        last_move_number = path[-1][0]
                        new_move_number = move[0]
                        if last_move_number == new_move_number:
                            continue
                    new_path = path + [move]
                    stack.append((new_path, new_board))
                    layer_quantity += 1
                    if len(new_path) > max_depth:
                        max_depth = len(new_path)
                    # pprint(stack)
            print(f"{smallest_f_gt_threshold = }")
            print(f"Looked through {layer_quantity} nodes, max depth = {max_depth}")


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
    solver.play()
