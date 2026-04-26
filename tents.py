import time
import tracemalloc
import problems
import os

from enum import IntEnum
from typing import Optional


problems_8 = [
    dict(
        rows=8,
        cols=8,
        row_clues=[1, 2, 2, 0, 2, 2, 2, 1],
        col_clues=[1, 1, 2, 1, 2, 1, 2, 2],
        trees=[
            (0, 6),
            (1, 2),
            (1, 7),
            (2, 5),
            (3, 1),
            (3, 4),
            (3, 6),
            (4, 0),
            (5, 4),
            (6, 2),
            (7, 1),
            (7, 6),
        ],
    ),
    dict(
        rows=8,
        cols=8,
        row_clues=[3, 1, 1, 2, 1, 1, 1, 2],
        col_clues=[2, 0, 4, 0, 2, 1, 1, 2],
        trees=[
            (0, 1),
            (0, 3),
            (1, 0),
            (1, 7),
            (2, 5),
            (3, 0),
            (3, 1),
            (4, 6),
            (5, 1),
            (6, 2),
            (7, 5),
            (7, 7),
        ],
    ),
    dict(
        rows=8,
        cols=8,
        row_clues=[4, 0, 1, 1, 2, 1, 2, 1],
        col_clues=[3, 0, 2, 1, 2, 0, 2, 2],
        trees=[
            (0, 1),
            (0, 3),
            (1, 0),
            (1, 7),
            (2, 7),
            (3, 0),
            (4, 3),
            (5, 2),
            (5, 5),
            (6, 6),
            (7, 0),
            (7, 3),
        ],
    ),
]


problems_10 = [
    dict(
        rows=10,
        cols=10,
        row_clues=[3, 1, 2, 3, 2, 2, 1, 3, 1, 2],
        col_clues=[3, 1, 2, 2, 1, 4, 1, 2, 1, 3],
        trees=[
            (0, 2),
            (0, 4),
            (0, 6),
            (1, 0),
            (1, 9),
            (2, 0),
            (2, 2),
            (2, 4),
            (3, 8),
            (4, 0),
            (4, 2),
            (4, 4),
            (5, 9),
            (7, 4),
            (7, 8),
            (8, 0),
            (8, 2),
            (8, 6),
            (9, 4),
            (9, 9),
        ],
    ),
    dict(
        rows=10,
        cols=10,
        row_clues=[3, 1, 2, 2, 1, 3, 1, 3, 1, 3],
        col_clues=[3, 2, 1, 2, 2, 3, 1, 1, 3, 2],
        trees=[
            (0, 3),
            (1, 1),
            (1, 5),
            (1, 9),
            (3, 2),
            (3, 4),
            (3, 7),
            (4, 0),
            (4, 1),
            (4, 6),
            (6, 0),
            (6, 3),
            (6, 4),
            (6, 7),
            (6, 8),
            (7, 8),
            (8, 4),
            (9, 1),
            (9, 6),
            (9, 7),
        ],
    ),
    dict(
        rows=10,
        cols=10,
        row_clues=[4, 1, 1, 2, 2, 1, 3, 1, 1, 4],
        col_clues=[3, 1, 2, 2, 2, 2, 3, 1, 2, 2],
        trees=[
            (0, 1),
            (0, 4),
            (0, 8),
            (1, 3),
            (1, 5),
            (1, 6),
            (3, 3),
            (4, 0),
            (4, 5),
            (4, 9),
            (5, 2),
            (7, 1),
            (7, 6),
            (7, 9),
            (8, 0),
            (8, 4),
            (8, 6),
            (9, 1),
            (9, 3),
            (9, 8),
        ],
    ),
]

problems = problems_8 + problems_10

class TentsDFS:
    # Ham khoi tao
    def __init__(self, rows, cols, trees, row_clues, col_clues):
        self.rows = rows # So hang cua ma tran
        self.cols = cols # So cot cua ma tran
        self.trees = trees # Danh sach toa do cua cay [(hang, cot), ...]
        self.row_clues = row_clues # So luong leu o moi dong
        self.col_clues = col_clues # So luong leu o moi cot
        self.tents = [] # Danh sach luu toa do cua leu [(hang, cot), ...]
        self.solution = None

    # Ham kiem tra vi tri leu hop le
    def is_valid_position(self, row, col):
        # Kiem tra vi tri hien tai cua leu co vuot qua ma tran hay trung vao cai cay nao khong
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        if (row, col) in self.trees:
            return False

        # Kiem tra so luong leu o hang va cot co vuot qua goi y hay khong
        row_count = 0
        col_count = 0
        for tent_r, tent_c in self.tents:
            if tent_r == row:
                row_count += 1
            if tent_c == col:
                col_count += 1
        if row_count >= self.row_clues[row]:
            return False
        if col_count >= self.col_clues[col]:
            return False

        # Kiem tra vi tri hien tai cua leu co cham vao leu khac hay khong (theo 8 huong)
        for tent_r, tent_c in self.tents:
            if abs(tent_r - row) <= 1 and abs(tent_c - col) <= 1:
                return False

        return True

    # Kiem tra so luong leu o moi hang va cot phai bang voi goi y
    def check_final_state(self):
        # Khoi tao mang de luu tong so leu o moi hang va cot
        row_counts = [0] * self.rows
        col_counts = [0] * self.cols

        # Dem so luong leu o moi hang va cot
        for tent_r, tent_c in self.tents:
            row_counts[tent_r] += 1
            col_counts[tent_c] += 1

        # Doi chieu ket qua voi goi y o moi hang
        for r in range(self.rows):
            if row_counts[r] != self.row_clues[r]:
                return False

        # Doi chieu ket qua voi goi y o moi cot
        for c in range(self.cols):
            if col_counts[c] != self.col_clues[c]:
                return False

        return True

    def solve(self, tree_index = 0, is_demo = False, delay = 0.5):
        # Neu da duyet het tat ca cay trong ma tran
        if tree_index == len(self.trees):
            if self.check_final_state() == True:
                self.solution = list(self.tents)
                return True
            return False

        # Lay toa do cay hien tai
        tree_r, tree_c = self.trees[tree_index]

        # Cac huong co the dat leu (trai, phai, duoi, tren)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Duyet tung huong xung quanh cay
        for dr, dc in directions:
            tent_r, tent_c = tree_r + dr, tree_c + dc
            # Kiem tra vi tri co hop le de dat leu khong
            if self.is_valid_position(tent_r, tent_c):
                self.tents.append((tent_r, tent_c)) # Push leu thoa dieu kien vao
                if is_demo:
                    self.print_demo_step("PUSH", tree_index, tent_r, tent_c, delay)
                if self.solve(tree_index + 1, is_demo, delay) == True:
                    return True # Goi de quy
                self.tents.pop() # Quay lui
                if is_demo:
                    self.print_demo_step("POP", tree_index, tent_r, tent_c, delay)

        return False

    # Ham in output
    def print_matrix(self):
        RESET = '\033[0m'
        GREEN = '\033[92m'   # Màu xanh lá cho Cây
        YELLOW = '\033[93m'  # Màu vàng cho Lều
        BLUE = '\033[94m'    # Màu xanh dương cho chữ và viền
        GRAY = '\033[90m'    # Màu xám cho đất trống

        print(f"{BLUE}Tents (T: Cây; A: Lều; .: Đất trống):{RESET}")
        print("    " + " ".join(str(c) for c in self.col_clues))
        print("   " + "-" * (self.cols * 2))

        for row in range(self.rows):
            row_str = []
            for col in range(self.cols):
                if (row, col) in self.trees:
                    # In Cây màu Xanh lá
                    row_str.append(f"{GREEN}T{RESET}")
                elif (row, col) in self.tents or (self.solution and (row, col) in self.solution):
                    # In Lều màu Vàng
                    row_str.append(f"{YELLOW}A{RESET}")
                else:
                    # In Đất trống màu Xám
                    row_str.append(f"{GRAY}.{RESET}")

            clue = self.row_clues[row]
            print(f"{BLUE}{clue}{RESET} | {' '.join(row_str)}")
        print("\n")

    def print_demo_step(self, action, tree_index, r, c, delay):
        os.system('cls' if os.name == 'nt' else 'clear')
        RESET = '\033[0m'
        CYAN = '\033[96m' # Xanh lơ cho bước Thử nghiệm
        RED = '\033[91m'  # Đỏ cho bước Quay lui

        if action == "PUSH":
            print(f"{CYAN}[*] THỬ NGHIỆM: Cắm lều cho cây số {tree_index + 1} tại ({r}, {c}){RESET}")
        elif action == "POP":
            print(f"{RED}[!] QUAY LUI: Sai hướng, nhổ lều của cây số {tree_index + 1} tại ({r}, {c}) lên{RESET}")

        self.print_matrix()
        time.sleep(delay)

class Cell(IntEnum):
    TENT = 0
    EMPTY = 1
    TREE = 2
    CANTPLACE = 3

class TentsHeuristic:
    def __init__(
        self,
        rows,
        columns,
        row_tents,
        column_tents,
        trees,
        demo=True,
    ):
        self.rows = rows
        self.columns = columns
        self.row_tents = [0] * rows
        self.column_tents = [0] * columns

        self.trees = trees

        self.grid = [[Cell.CANTPLACE] * columns for _ in range(rows)]
        self.current_row_tents = [0] * rows
        self.current_column_tents = [0] * columns

        self.history: list[tuple[int, int]] = []
        self.no_tents = len(trees)

        self.demo = demo

        self.slots = []

        self.start_time = 0.0

        self.column_tents = column_tents
        self.row_tents = row_tents

        for r, c in trees:
            self.grid[r][c] = Cell.TREE

            for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
                nr = r + dr
                nc = c + dc

                if (
                    self.in_bound(nr, nc)
                    and self.column_tents[nc]
                    and self.row_tents[nr]
                    and self.grid[nr][nc] != Cell.TENT
                ):
                    self.grid[nr][nc] = Cell.EMPTY

        for r in range(self.rows):
            for c in range(self.columns):
                if self.grid[r][c] == Cell.EMPTY:
                    self.slots.append((r, c))

    def in_bound(self, r: int, c: int):
        return r >= 0 and r < self.rows and c >= 0 and c < self.rows

    # If it's possible to add a tent here, it returns a Commit,
    # which can be committed onto the grid.
    def try_add_tent(self, r: int, c: int) -> Optional[tuple[int, int]]:
        if self.grid[r][c] != Cell.EMPTY:
            return None

        if (
            self.current_column_tents[c] >= self.column_tents[c]
            or self.current_row_tents[r] >= self.row_tents[r]
        ):
            return None

        for dr in [-1, 0, 1]:
            nr = r + dr

            if nr < 0 or nr >= self.rows:
                continue

            for dc in [-1, 0, 1]:
                if dc == 0 and dr == 0:
                    continue

                nc = c + dc

                if nc < 0 or nc >= self.columns:
                    continue

                if self.grid[nr][nc] == Cell.TENT:
                        return None

        return r, c

    # Applies commit onto grid
    def commit(self, commit: tuple[int, int]):
        self.history.append(commit)
        r, c = commit

        self.grid[r][c] = Cell.TENT

        self.current_row_tents[r] += 1
        self.current_column_tents[c] += 1

    # Revert to the prevous commit
    def revert(self):
        commit = self.history.pop()

        r, c = commit
        self.grid[r][c] = Cell.EMPTY

        self.current_row_tents[r] -= 1
        self.current_column_tents[c] -= 1

    def draw(self):
        print("  ", end="")
        for n in self.column_tents:
            print(f"{n} ", end="")

        print()

        for r in range(self.rows):
            n = self.row_tents[r]
            print(f"{n} ", end="")
            for c in range(self.columns):
                char = "_"
                match self.grid[r][c]:
                    case Cell.TREE:
                        char = "T"
                    case Cell.TENT:
                        char = "A"
                    case Cell.CANTPLACE:
                        char = " "
                    case _:
                        char = "."
                print(f"{char} ", end="")
            print()

    def draw_solution(self):
        grid = [[Cell.CANTPLACE] * self.columns for _ in range(self.rows)]

        for r, c in self.history:
            grid[r][c] = Cell.TENT

        for r, c in self.trees:
            grid[r][c] = Cell.TREE

        print("  ", end="")
        for n in self.column_tents:
            print(f"{n} ", end="")

        print()

        for r in range(self.rows):
            n = self.row_tents[r]
            print(f"{n} ", end="")
            for c in range(self.columns):
                char = "_"
                match self.grid[r][c]:
                    case Cell.TREE:
                        char = "T"
                    case Cell.TENT:
                        char = "A"
                    case Cell.CANTPLACE:
                        char = " "
                    case _:
                        char = "."
                print(f"{char} ", end="")
            print()

    def solve(
        self,
        tents_no: int = 0,
        start=0,
        current_r=0,
    ) -> bool:
        if tents_no >= self.no_tents:
            return True

        for i in range(start, len(self.slots) - self.no_tents + tents_no + 1):
            r, c = self.slots[i]

            if r > current_r:
                # bail out if the previous row has an incorrect number of tents.
                for _r in range(current_r, r):
                    if self.current_row_tents[_r] != self.row_tents[_r]:
                        return False

                current_r = r

            if commit := self.try_add_tent(r, c):
                self.commit(commit)

                if self.demo:
                    game.draw()
                    print()
                    # input()
                    time.sleep(0.3)
            else:
                continue

            if self.solve(tents_no + 1, i + 1, r):
                return True

            self.revert()

        return False

if __name__ == "__main__":
    print("--- DPS ---")

    for i, problem in enumerate(problems):
        rows = problem["rows"]
        cols = problem["cols"]
        row_clues = problem["row_clues"]
        col_clues = problem["col_clues"]
        trees = problem["trees"]

        game = TentsDFS(rows, cols, trees, row_clues, col_clues)

        tracemalloc.start()
        start_time = time.time()

        is_solved = game.solve(is_demo=False)

        end_time = time.time()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        if is_solved:
            game.print_matrix()
            print(f"Thời gian thực thi : {(end_time - start_time) * 1000:.4f} ms")
            print(f"Bộ nhớ tiêu tốn (Peak) : {peak_mem / 1024:.4f} KB")
        else:
            print("Khong tim thay giai phap")


    print("--- HEURISTIC ---")

    for i, problem in enumerate(problems):
        # for i, problem in enumerate(problems.problems_8):
        rows = problem["rows"]
        cols = problem["cols"]
        row_clues = problem["row_clues"]
        col_clues = problem["col_clues"]
        trees = problem["trees"]
        print(f"\nPROBLEM {i + 1}")

        game = TentsHeuristic(rows, cols, row_clues, col_clues, trees, demo=False)

        tracemalloc.start()
        start_time = time.time()

        solved = game.solve()

        end_time = time.time()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        if solved:
            print("Solution found:")
            game.draw_solution()
            print()
        else:
            print("No solution found")

        if not game.demo:
            print(f"Time taken: {(end_time - start_time) * 1000:.4f}ms")
            print(f"Peak memory usage : {peak_mem / 1024:.4f} KB")
