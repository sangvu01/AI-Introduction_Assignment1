import math
import time
import tracemalloc
from functools import reduce

DEMO = True
# 8 7 1 9 4 3 2 5 6
# 6 3 9 1 2 5 7 8 4
# 5 4 2 8 6 7 9 1 3
# 2 5 8 7 1 6 4 3 9
# 4 1 3 5 9 2 8 6 7
# 7 9 6 3 8 4 5 2 1
# 9 8 5 4 3 1 6 7 2
# 1 2 7 6 5 9 3 4 8
# 3 6 4 2 7 8 1 9 5

# ------------ ----------- ------------
# ------------ Data Models ------------
# ------------ ----------- ------------
class Blind_Cell:
    """
    The starting building block of a Sudoku grid

    Attributes:
        row, col    : 0-indexed row/col position
        value       : 0 if empty, 1..N otherwise
        cage_id     : which cage this cell belongs to (-1 until assigned)
    """
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.value: int = 0
        self.cage_id: int = -1

    def is_empty(self) -> bool:
        return self.value == 0

    def __repr__(self) -> str:
        return f"Cell({self.row},{self.col})={'.' if self.value == 0 else self.value}"


class Blind_Cage:
    """
    A cage containing many cells, with a given sum
    No number appears more than once in a cage

    Attributes:
        cage_id     : unique identifier
        target      : required sum of all cell values
        cells       : list of Blind_Cell objects inside this cage
    """
    def __init__(self, cage_id: int, target: int, cells: list[Blind_Cell]):
        self.cage_id = cage_id
        self.target = target
        self.cells = cells
        for cell in self.cells:
            cell.cage_id = cage_id

    @property
    def current_sum(self) -> int:
        return sum(c.value for c in self.cells if not c.is_empty())

    @property
    def is_complete(self) -> bool:
        return all(not c.is_empty() for c in self.cells)

    @property
    def is_valid(self) -> bool:
        filled = [c.value for c in self.cells if not c.is_empty()]
        if len(filled) != len(set(filled)):
            return False
        if self.is_complete:
            return self.current_sum == self.target
        return self.current_sum <= self.target


class Blind_Grid:
    """
    A N x N grid representing the game board
    N must be a perfect square (4, 9, 16, ...)

    Attributes:
        n           : board dimension
        box_size    : sub-box dimension = sqrt(n)
        cages:      : list of all Blind_Cage objects
        cells       : 2D list of Blind_Cell objects [row][col]
    """
    def __init__(self, n: int, cages: list[Blind_Cage]):
        self.n = n
        self.box_size = math.isqrt(n)
        self.cages = cages
        self.cells = [[Blind_Cell(r, c) for c in range(n)] for r in range(n)]

        for cage in self.cages:
            cage.cells = [self.cells[cell.row][cell.col] for cell in cage.cells]
            for cell in cage.cells:
                cell.cage_id = cage.cage_id

        self.cell_to_cage = {
            (cell.row, cell.col): cage
            for cage in self.cages
            for cell in cage.cells
        }

    def get_cage(self, row: int, col: int) -> Blind_Cage:
        return self.cell_to_cage[(row, col)]

    def all_peers(self, row: int, col: int) -> set[Blind_Cell]:
        # Row peers
        peers = set(self.cells[row])

        # Add in col peers
        peers.update(self.cells[r][col] for r in range(self.n))

        # Add in box peers
        br, bc = (row // self.box_size) * self.box_size, (col // self.box_size) * self.box_size
        peers.update(self.cells[br + dr][bc + dc] for dr in range(self.box_size) for dc in range(self.box_size))

        peers.discard(self.cells[row][col])
        return peers

    def is_solved(self) -> bool:
        all_filled = all(not self.cells[r][c].is_empty() for r in range(self.n) for c in range(self.n))
        return all_filled and all(cage.is_valid for cage in self.cages)

    def __str__(self) -> str:
        lines = []
        for r in range(self.n):
            lines.append(" ".join(str(self.cells[r][c].value) if not self.cells[r][c].is_empty() else "." for c in range(self.n)))
            if (r + 1) % self.box_size == 0 and r + 1 < self.n:
                lines.append("-" * (self.n * 2 - 1))
        return "\n".join(lines)


# ------------ ------ ------------
# ------------ Parser ------------
# ------------ ------ ------------
def parse(input_data: list) -> Blind_Grid:
    max_coord = max(max(r, c) for _, coords in input_data for r, c in coords)
    n = max_coord + 1
    cages = [Blind_Cage(i, target, [Blind_Cell(r, c) for r, c in coords]) for i, (target, coords) in enumerate(input_data)]
    return Blind_Grid(n, cages)


# ------------ ------------------ ------------
# ------------ Naive Backtracking ------------
# ------------ ------------------ ------------
def solve_naive(grid: Blind_Grid) -> bool:
    cell = _first_empty(grid)
    if cell is None:
        return True

    for digit in range(1, grid.n + 1):
        cell.value = digit
        if _naive_ok(grid, cell):
            if solve_naive(grid):
                return True
        cell.value = 0
    return False

def _first_empty(grid: Blind_Grid) -> Blind_Cell | None:
    for r in range(grid.n):
        for c in range(grid.n):
            if grid.cells[r][c].is_empty():
                return grid.cells[r][c]
    return None

def _naive_ok(grid: Blind_Grid, cell: Blind_Cell) -> bool:
    for peer in grid.all_peers(cell.row, cell.col):
        if peer.value == cell.value:
            return False
    return grid.get_cage(cell.row, cell.col).is_valid


# ------------ --------- ------------
# ------------ Benchmark ------------
# ------------ --------- ------------
def benchmark(input_data: list, label: str, timeout: float = 60.0):
    print(f"\n  {label}")
    print(f"  {'─'*52}")
    print(f"  {'solver':14} {'result':10} {'time':12} {'peak memory'}")
    print(f"  {'─'*52}")

    grid = parse(input_data)
    tracemalloc.start()
    start_time = time.monotonic()

    try:
        solved = solve_naive(grid)
    except RecursionError:
        solved = False

    elapsed = time.monotonic() - start_time
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    status = "solved" if solved and grid.is_solved() else "failed"
    mem = f"{peak/1024:.0f} KB" if peak/1024 < 1024 else f"{peak/(1024*1024):.2f} MB"

    print(f"  {'naive':14} {status:10} {elapsed:.4f}s     {mem}")
    if solved:
        print("\n  Solution:")
        print(grid)


# ------------ ------- ------------
# ------------ Puzzles ------------
# ------------ ------- ------------
PUZZLE_4x4 = [
    (7, [(0,0), (0,1), (0,2)]),
    (5, [(0,3), (1,3)]),
    (7, [(1,0), (1,1)]),
    (3, [(1,2), (2,2)]),
    (6, [(2,0), (3,0)]),
    (4, [(2,1), (3,1)]),
    (8, [(2,3), (3,2), (3,3)])
]
# 1 2 4 3
# 3 4 1 2
# 4 3 2 1
# 2 1 3 4
PUZZLE_4x4_vip = [
    (3, [(0, 0), (0, 1)]), 
    (7, [(0, 2), (0, 3)]), 
    (7, [(1, 0), (1, 1)]), 
    (3, [(1, 2), (1, 3)]), 
    

    (4, [(2, 0), (3, 0)]),  
    (6, [(2, 1), (3, 1)]), 
    (6, [(2, 2), (3, 2)]), 
    (4, [(2, 3), (3, 3)])
]
# 2 1 3 4
# 4 3 1 2
# 1 2 4 3
# 3 4 2 1

input_data = [
    (18, [(0, 0), (0, 1), (1, 1)]), (10, [(0, 2), (1, 2)]), (16, [(0, 3), (0, 4), (0, 5)]), (9, [(0, 6), (1, 6)]), (13, [(0, 7), (1, 7)]), (10, [(0, 8), (1, 8)]), (13, [(1, 0), (2, 0), (3, 0)]), (3, [(1, 3), (1, 4)]), (12, [(1, 5), (2, 5)]), (9, [(2, 1), (3, 1)]), (10, [(2, 2), (3, 2)]), (15, [(2, 3), (3, 3)]), (21, [(2, 4), (3, 4), (4, 3), (4, 4)]), (19, [(2, 6), (3, 5), (3, 6)]), (13, [(2, 7), (2, 8), (3, 8)]), (9, [(3, 7), (4, 7)]), (20, [(4, 0), (5, 0), (6, 0)]), (4, [(4, 1), (4, 2)]), (14, [(4, 5), (5, 4), (5, 5)]), (13, [(4, 6), (5, 6)]), (8, [(4, 8), (5, 8)]), (15, [(5, 1), (5, 2)]), (7, [(5, 3), (6, 3)]), (15, [(5, 7), (6, 6), (6, 7)]), (13, [(6, 1), (6, 2)]), (13, [(6, 4), (6, 5), (7, 5)]), (14, [(6, 8), (7, 7), (7, 8)]), (3, [(7, 0), (7, 1)]), (20, [(7, 2), (8, 0), (8, 1), (8, 2)]), (8, [(7, 3), (8, 3)]), (24, [(7, 4), (7, 6), (8, 4), (8, 5), (8, 6)]), (14, [(8, 7), (8, 8)])
]
PUZZLE_9x9 = [
    (6, [(0,0), (0,1)]),
    (12, [(0,2), (0,3)]),
    (11, [(0,4), (0,5)]),
    (17, [(0,6), (0,7), (1,7)]),
    (4, [(0,8), (1,8)]),
    (7, [(1,0), (1,1)]),
    (16, [(1,2), (2,2), (2,3)]),
    (15, [(1,3), (1,4)]),
    (8, [(1,5), (2,4), (2,5)]),
    (13, [(1,6), (2,6)]),
    (15, [(2,0), (2,1)]),
    (11, [(2,7), (2,8)]),
    (10, [(3,0), (4,0)]),
    (19, [(3,1), (4,1), (5,1)]),
    (14, [(3,2), (4,2), (4,3)]),
    (12, [(3,3), (3,4)]),
    (7, [(3,5), (3,6)]),
    (7, [(3,7), (3,8)]),
    (6, [(4,4), (4,5)]),
    (5, [(4,6), (5,6)]),
    (12, [(4,7), (5,7)]),
    (16, [(4,8), (5,8)]),
    (8, [(5,0), (6,0)]),
    (14, [(5,2), (5,3), (6,3)]),
    (12, [(5,4), (6,4)]),
    (14, [(5,5), (6,5)]),
    (16, [(6,1), (6,2), (7,2)]),
    (7, [(6,6), (7,6)]),
    (11, [(6,7), (6,8)]),
    (10, [(7,0), (7,1)]),
    (7, [(7,3), (7,4)]),
    (19, [(7,5), (8,4), (8,5)]),
    (27, [(7,7), (7,8), (8,6), (8,7), (8,8)]),
    (10, [(8,0), (8,1)]),
    (7, [(8,2), (8,3)])
]

class Heuristic_Cell:
    def __init__(self, r, c, size):
        self.r = r
        self.c = c
        self.value = 0
        self.valid_nums = set(range(1, size + 1))
        self.cage = None

    def __str__(self):
        vals = sorted(list(self.valid_nums))
        return f"Cell: {self.r}, {self.c} | Value: {self.value} | valid nums: {vals}"

class Heuristic_Cage:
    def __init__(self, target_sum, position):
        self.target_sum = target_sum
        self.position = position
        self.cells = []

    def current_sum(self):
        return sum(cell.value for cell in self.cells)

    def number_of_remaining_cells(self):
        return sum(1 for cell in self.cells if cell.value == 0)

class Heuristic_KillerSudoku:
    def __init__(self, size, cage_defs):
        self.size = size
        self.grid = [[Heuristic_Cell(r, c, size) for c in range(size)] for r in range(size)]
        self.cages = []

        for target_sum, position in cage_defs:
            current_cage = Heuristic_Cage(target_sum, position)
            for r, c in position:
                cell = self.grid[r][c]
                cell.cage = current_cage
                current_cage.cells.append(cell)
            self.cages.append(current_cage)


    def is_valid_refined(self, cell: Heuristic_Cell, val):
        for r in range(self.size):
            if( r == cell.r):
                continue
            if(self.grid[r][cell.c].value == val):
                return False

        for c in range(self.size):
            if( c == cell.c):
                continue
            if(self.grid[cell.r][c].value == val):
                return False

        box_size = int(self.size**0.5)
        start_r = (cell.r // box_size) * box_size
        start_c = (cell.c // box_size) * box_size

        for c in range(start_c, start_c + box_size):
            for r in range(start_r, start_r + box_size):
                if (c == cell.c) and (r == cell.r) :
                    continue
                if(self.grid[r][c].value == val):
                    return False

        cage_of_cell = cell.cage
        new_sum = cage_of_cell.current_sum() + val

        if(new_sum > cage_of_cell.target_sum):
            return False

        remained_cells_in_cage = cage_of_cell.number_of_remaining_cells()
        if remained_cells_in_cage == 1:
            return new_sum == cage_of_cell.target_sum

        remained_sum = cage_of_cell.target_sum - new_sum
        remained_cells_in_cage -= 1 # After fill the val
        min_possible = reduce(lambda prev, curr: prev + curr, range(1, remained_cells_in_cage + 1), 0)
        max_possible = reduce(lambda prev, curr: prev + curr, range(self.size - remained_cells_in_cage + 1, self.size + 1), 0)

        if (remained_sum < min_possible) or (remained_sum > max_possible):
            return False

        return True


    def refresh_valid_nums(self):
        for r in range(self.size):
            for c in range(self.size):
                cell = self.grid[r][c]
                # Set comprehension:
                # valid_num = list(set(i for i in range(1, self.size + 1) if self.is_valid_refined(cell, i)))
                if (cell.value == 0):
                    valid_num = set()
                    for i in range(1, self.size + 1):
                        if(self.is_valid_refined(cell, i)):
                            valid_num.add(i)
                    cell.valid_nums = valid_num
                else:
                    cell.valid_nums = set()


    def solve(self):
        best_cell = None
        min_valid_nums_size = self.size + 1
        self.refresh_valid_nums()

        if DEMO:
            print("-----------------------")
            self.print_grid()

        for r in range(self.size):
            for c in range(self.size):
                if (self.grid[r][c].value == 0):
                    valid_nums_size = len(self.grid[r][c].valid_nums)
                    if (valid_nums_size < min_valid_nums_size):
                        min_valid_nums_size = valid_nums_size
                        best_cell = self.grid[r][c]
                    if (min_valid_nums_size == 0):
                        return False

        if (best_cell is None):
            return True

        nums = sorted(list(best_cell.valid_nums))

        for num in nums:
            if DEMO:
                print(f"\n\nĐiền ô ({best_cell.r}, {best_cell.c}): {num}")
            all_of_old_valid_nums = [[self.grid[r][c].valid_nums for c in range(self.size)] for r in range(self.size)]
            best_cell.value = num

            self.refresh_valid_nums()

            if self.solve():
                return True
            if DEMO:
                print("##########\n SAIIIIII !!!!!!!!!!!!!!!!\nChạy lại:")
                print(f"##########_ SAIIIIII !!!!!!!!!!!!!!!! -> Quay lui tại ({best_cell.r}, {best_cell.c}) = {num}")


            best_cell.value = 0
            for r in range(self.size):
                for c in range(self.size):
                    self.grid[r][c].valid_nums = all_of_old_valid_nums[r][c]
        return False

    def print_grid(self):
        for row in self.grid:
            print(" ".join(str(cell.value) for cell in row))
        if DEMO:
            for row in self.grid:
                for cell in row:
                    if cell.value == 0 or True:
                        print(cell)
input_data = [
    (5, [(0, 0), (0, 1)]), 
    
    (6, [(0, 2), (0, 3), (1, 3)]), 
    (5, [(1, 0), (2, 0)]), 
    (10, [(1, 1), (2, 1), (3, 0), (3, 1)]), (7, [(1, 2), (2, 2)]), (7, [(2, 3), (3, 2), (3, 3)])
]
if __name__ == "__main__":
    print("=" * 56)
    print("  KILLER SUDOKU — NAIVE SOLVER BENCHMARK")
    print("=" * 56)

    # benchmark(PUZZLE_4x4, label="4x4 — 8 cages")
    # benchmark(PUZZLE_9x9, label="9x9 — 35 cages")
    # Note: 9x9 naive can take a long time


    # print()
    # print()
    # print("=" * 56)
    # print("  KILLER SUDOKU — HEURISTIC SOLVER")
    # print("=" * 56)
    # benchmark(input_data, "")
    # benchmark(PUZZLE_9x9, "")

    for input_data in [input_data]:
        print()

        sum_grid = reduce(lambda prev, curr: curr[0] + prev, input_data, 0)
        size = int((sum_grid + 252) / 73) #sum = (1+2+3+4)*4 = 40 -> size = 4; sum = (1+2+3+4+5+6+7+8+9)*9 = 405 -> size = 9


        sudoku = Heuristic_KillerSudoku(size, input_data)
        sudoku.print_grid()
        print("START SOLVING...")


        # grid = parse(input_data)
        # tracemalloc.start()
        # start_time = time.monotonic()

        solved = sudoku.solve()

        if solved:
            print("Đáp án:")
            sudoku.print_grid()
        else:
            print("Không có lời giải !!!")


        # elapsed = time.monotonic() - start_time
        # _, peak = tracemalloc.get_traced_memory()
        # tracemalloc.stop()

        # status = "solved" if solved else "failed"
        # mem = f"{peak/1024:.0f} KB" if peak/1024 < 1024 else f"{peak/(1024*1024):.2f} MB"

        # print(f"  {'heuristic':14} {status:10} {elapsed:.4f}s     {mem}")
