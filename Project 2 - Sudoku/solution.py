# CS3243 Introduction to Artificial Intelligence
# Project 2

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.size = len(puzzle)
        self.domains = {}
        self.constraints = None

    def solve(self):
        return solvePuzzle(self.puzzle, {})


    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.
def getgroupset(puzzle, groupx, groupy):
    s = set()
    for i in range(3 * groupx, 3 * (groupx + 1)):
        for j in range(3 * groupy, 3 * (groupy + 1)):
            s.add(puzzle[i][j])
    return s
def transpose(puzzle):
    lst = []
    for col in range(len(puzzle[0])):
        column = []
        for row in puzzle:
            column.append(row[col])
        lst.append(column)
    return lst
def check(puzzle):
    s = set()
    #Check rows
    for row in puzzle:
        s.clear()
        for value in row:
            s.add(value)
        if list(s) != [1,2,3,4,5,6,7,8,9]:
            return False
    #Check columns
    grid = transpose(puzzle)
    for column in grid:
        s.clear()
        for value in column:
            s.add(value)
        if list(s) != [1,2,3,4,5,6,7,8,9]:
            return False

    #Check groups (3x3 squares)
    for groupx in range(3):
        for groupy in range(3):
            s = getgroupset(puzzle, groupx, groupy)
            if list(s) != [1,2,3,4,5,6,7,8,9]:
                return False
    return True

def pickUnassignedValue(puzzle, inference):
    # if (inference == {}):
    # for i in range(len(puzzle)):
    #     for j in range(len(puzzle)):
    #         if (puzzle[i][j] ==0):
    #             return (i, j)
    pair = list(inference.items())
    if (pair == []):
        pair.sort(key = lambda x: len(x[1]), reverse = True)
    for i in pair:
        if (puzzle[i[0][0]][i[0][1]] == 0):
            # print(i[0])
            # raise ValueError("1")
            return i[0]
    return False

def orderDomainValue(var, puzzle, inference):
    varx = var[0]
    vary = var[1]
    possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for unit in puzzle[varx]:
        if (unit in possible):
            possible.remove(unit)
    for row in puzzle:
        if (row[vary] in possible):
            possible.remove(row[vary])
    groupx = int(varx / 3)
    groupy = int(vary / 3)
    s = getgroupset(puzzle, groupx, groupy)
    for i in s:
        if (i in possible):
            possible.remove(i)

    if (var in inference):
        for i in inference[var]:
            possible.remove(i)
    if (len(possible) == 0):
        return False
    return possible

def computeDomain(x, inference):
    possible = []
    restriction = []
    if (x in inference):
        restriction = inference[x]
    for i in range(1, 10):
        if (i not in restriction):
            possible.append(i)
    return possible


def infer(grid, var, infer):
    if (infer == {}):
        return {}
    num = grid[var[0]][var[1]]
    for x_col in range(len(puzzle)):
        i = var[0]
        j = x_col
        if grid[i][j]:
            continue
        if ((i,j) not in infer):
            continue
        if num not in infer[(i,j)]:
            remain = len(infer[(i,j)]) + 1
            infer[(i,j)].append(num)
        else: #already constrained before
            continue

        # If no remaining values left, invalid assignment
        if remain == 9:
            return False
    for x_row in range(len(puzzle)):
        i = x_row
        j = var[1]
        if grid[i][j]:
            continue
        if ((i,j) not in infer):
            continue
        if num not in infer[(i,j)]:
            remain = len(infer[(i,j)]) + 1
            infer[(i,j)].append(num)
        else: #already constrained before
            continue

        # If no remaining values left, invalid assignment
        if remain == 9:
            return False
    groupx = int(var[0] / 3)
    groupy = int(var[1] / 3)
    for x_row in range(groupx * 3, (groupx + 1) * 3):
        for x_col in range(groupy * 3, (groupy + 1) * 3):
            i = x_row
            j = x_col
            if grid[i][j]:
                continue
            if ((i,j) not in infer):
                continue
            if num not in infer[(i,j)]:
                remain = len(infer[(i,j)]) + 1
                infer[(i,j)].append(num)
            else: #already constrained before
                continue

            # If no remaining values left, invalid assignment
            if remain == 9:
                return False
    # skip if already assigned

    # inference = infer
    # varQueue = [var]
    # transpose_grid = transpose(grid)
    # while (len(varQueue) != 0):
    #     y = varQueue.pop()
    #     #Row constraint
    #     for x_col in range(len(puzzle)):
    #         if (x_col == y[1]):
    #             continue
    #         unit = (y[0], x_col)
    #         S = computeDomain(unit, inference)
    #         s = getgroupset(puzzle, int(unit[0] / 3), int(unit[1] / 3))
    #         for v in S:
    #             if (v in grid[unit[0]] or v in transpose_grid[unit[1]] or v in s):
    #                 if (unit in inference):
    #                     inference[unit].append(v)
    #                 else:
    #                     inference[unit] = [v]
    #         T = computeDomain(unit, inference)
    #         if (len(T) == 0):
    #             return False
    #         if (S != T):
    #             varQueue.append(unit)

    #     #Column constraint
    #     for x_row in range(len(puzzle)):
    #         if (x_row == y[0]):
    #             continue
    #         unit = (x_row, y[1])
    #         S = computeDomain(unit, inference)
    #         s = getgroupset(puzzle, int(unit[0] / 3), int(unit[1] / 3))
    #         for v in S:
    #             if (v in grid[unit[0]] or v in transpose_grid[unit[1]] or v in s):
    #                 if (unit in inference):
    #                     inference[unit].append(v)
    #                 else:
    #                     inference[unit] = [v]
    #         T = computeDomain(unit, inference)
    #         if (len(T) == 0):
    #             return False
    #         if (S != T):
    #             varQueue.append(unit)

    #     #Group constraint
    #     groupx = int(var[0] / 3)
    #     groupy = int(var[1] / 3)
    #     s = getgroupset(puzzle, groupx, groupy)
    #     for x_row in range(groupx * 3, (groupx + 1) * 3):
    #         for x_col in range(groupy * 3, (groupy + 1) * 3):
    #             if (x_row == y[0] and x_col == y[1]):
    #                 continue
    #             unit = (x_row, x_col)
    #             S = computeDomain(unit, inference)
    #             for v in S:
    #                 if (v in grid[unit[0]] or v in transpose_grid[unit[1]] or v in s):
    #                     if (unit in inference):
    #                         inference[unit].append(v)
    #                     else:
    #                         inference[unit] = [v]
    #             T = computeDomain(unit, inference)
    #             if (len(T) == 0):
    #                 return False
    #             if (S != T):
    #                 varQueue.append(unit)
    #     # print("The length is now")
    #     # print(len(varQueue))

    # return inference


def solvePuzzle(puzzle, inference):
    if (check(puzzle)):
        return puzzle
    var = pickUnassignedValue(puzzle, inference)
    if (var == False):
        return False
    val_list = orderDomainValue(var, puzzle, inference)
    if (val_list == False):
        return False
    for val in val_list:
        varx = var[0]
        vary = var[1]
        puzzle[varx][vary] = val
        new_inference = infer(puzzle, var, inference)
        if (new_inference != False):
            res = solvePuzzle(puzzle, new_inference)
            if (res != False):
                return res
        puzzle[varx][vary] = 0
    return False
def copy_deep(infer):
    inference = {}
    for i in infer.keys():
        inference[i] = [];
        inference[i].extend(infer[i])
    return inference


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
